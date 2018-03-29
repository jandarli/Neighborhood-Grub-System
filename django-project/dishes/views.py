import decimal

from django.db.models import Avg
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from watson_developer_cloud import AlchemyLanguageV1
from collections import Counter

from dishes.models import (
    DishPost, Diner, Order, DishRequest, Chef, Bid,
    OrderFeedback, RateChef, RateDiner, Dish, Rating,
    Offer
)
from dishes.forms import (
    DishForm, DishRequestForm, DishPostForm,
    ChefForm, FeedbackForm, RateChefForm,
    RateDinerForm, RatingForm, BidForm, OfferForm
)

from accounts.models import RedFlag, Complaint
from accounts.forms import ComplaintForm



# Getting APIKEY variable from settings.py
APIKEY = getattr(settings, "APIKEY", None)

# Watson authentication
alchemy_language = AlchemyLanguageV1(api_key=APIKEY)

def posts(request):
    dish_posts = DishPost.objects.filter(status=DishPost.OPEN)
    is_chef = hasattr(request.user, "chef")
    context = {"dish_posts": dish_posts, "is_chef": is_chef}
    return render(request, "dishes/posts.html", context)

def post_detail(request, dish_post_id):
    context = {}
    diner = request.user.diner
    dish_post = get_object_or_404(DishPost, pk=dish_post_id)
    if request.method == "POST":
        form = BidForm(request.POST)
        if form.is_valid():
            # Verify the bid price is not less than the asking price.
            # Verify the bid num servings is not greater than the
            # available number of servings.
            bid_price = form.cleaned_data["price"]
            nservings = form.cleaned_data["num_servings"]
            total = bid_price*nservings
            balance = diner.user.balance
            if bid_price >= dish_post.min_price and\
               nservings <= dish_post.available_servings() and\
               total <= balance.amount:
                # Create the corresponding bid.
                bid_data = {
                    "price": bid_price,
                    "num_servings": nservings,
                    "diner": diner,
                    "dish_post": dish_post
                }
                Bid.objects.create(**bid_data)
                return redirect("orders_and_requests")
            else:
                context["message"] = ("Bid price must not be less than "
                                      "the minimum price, the requested "
                                      "number of servings cannot be more "
                                      "than the available number of servings "
                                      "and you must have sufficient funds to "
                                      "place this bid.")
    else:
        form = BidForm()
    context["dish_post"] = dish_post
    context["form"] = form
    if request.user.is_authenticated:
        context["user"] = request.user
    return render(request, "dishes/post_detail.html", context)

def order_dish(request, dish_post_id):
    diner = Diner.objects.get(user=request.user)
    dish_post = DishPost.objects.get(pk=dish_post_id)
    num_servings = request.POST["num_servings"]
    order = Order.objects.create(diner=diner,
                                 dish_post=dish_post,
                                 num_servings=num_servings)
    return redirect("orders_and_requests")

def orders_and_accepted_requests(request):
    if not request.user.is_authenticated:
        return redirect("dishes")
    else:
        diner = request.user.diner
        orders = diner.order_set

        pending_orders = orders.filter(status__lt=Order.CANCELLED)
        closed_orders = orders.filter(status__gte=Order.CANCELLED)

        diner_requests = diner.dishrequest_set
        pending_requests = diner_requests.filter(status=DishRequest.ACCEPTED)
        closed_requests = diner_requests.filter(status__gt=DishRequest.ACCEPTED)

        is_chef = hasattr(request.user, "chef")

        context = {
            "DishPost": DishPost,
            "orders": pending_orders,
            "has_history": closed_orders.count() or closed_requests.count(),
            "requests": pending_requests,
            "is_chef": is_chef
        }
        return render(request, "dishes/orders-requests.html", context)

def orders_and_requests_history(request):
    if not request.user.is_authenticated:
        return redirect("dishes")
    else:
        diner = request.user.diner

        orders = diner.order_set.filter(status__gt=Order.OPEN)
        requests = diner.dishrequest_set.filter(status__gt=DishRequest.OPEN)

        context = {
            "orders": orders,
            "requests": requests
        }

        return render(request, "dishes/orders-requests-history.html", context)

def requests(request):
    dish_requests = DishRequest.objects.filter(status=DishRequest.OPEN)
    context = {"dish_requests": dish_requests}
    return render(request, "dishes/requests.html", context)

def request_offers(request, dish_request_id):
    dish_request = get_object_or_404(DishRequest, pk=dish_request_id)
    offers = dish_request.offer_set.filter(status=Offer.PENDING)
    context = {
        "dish_request": dish_request,
        "offers": offers
    }
    return render(request, "dishes/request_offers.html", context)

def reject_offer(request, dish_request_id, offer_id):
    if request.method == "POST":
        offer = get_object_or_404(Offer, pk=offer_id)
        offer.status = Offer.REJECTED
        offer.save()
    return redirect("requests_offers", dish_request_id)

def accept_offer(request, dish_request_id, offer_id):
    if request.method == "POST":
        dish_request = get_object_or_404(DishRequest, pk=dish_request_id)
        offer = get_object_or_404(Offer, pk=offer_id)
        # Verify the diner has the money.
        diner_balance = request.user.balance
        chef_balance = offer.chef.user.balance
        if diner_balance.is_vip:
            total = decimal.Decimal(0.90) * offer.total()
        else:
            total = offer.total()
        if diner_balance.amount < total:
            offers = dish_request.offer_set.filter(status=Offer.PENDING)
            context = {
                "dish_request": dish_request,
                "offers": offers,
                "message": "You must have sufficient funds to accept an offer."
            }
            return render(request, "dishes/requests_offers.html", context)
        # Update the offer status
        offer.status = Offer.ACCEPTED
        for offr in offer.dish_request.offer_set.all():
            if offr != offer:
                offr.status = Offer.REJECTED
                offr.save()
        offer.save()
        dish_request.status = DishRequest.ACCEPTED
        dish_request.save()
        # Transfer the money.
        diner_balance.debit(total)
        chef_balance.credit(offer.total())
    return redirect("orders_and_requests")

def request_detail(request, dish_request_id):
    context = {}
    user = request.user
    dish_request = get_object_or_404(DishRequest, pk=dish_request_id)
    if request.method == "POST":
        form = OfferForm(request.POST)
        if form.is_valid():
            # Verify that the price is greater or equal to the min price.
            offer_price = form.cleaned_data["price"]
            if offer_price >= dish_request.min_price:
                # Create the Offer
                Offer.objects.create(chef=user.chef,
                                     dish_request=dish_request,
                                     price=offer_price)
                return redirect("list-requests")
            else:
                context["message"] = ("The offer price must be greater "
                                      "or equal to the minimum price.")
    else:
        form = OfferForm()
    if user.is_authenticated:
        context["user"] = user
    context["dish_request"] = dish_request
    context["is_chef"] = hasattr(request.user, "chef")
    context["form"] = form
    return render(request, "dishes/request_detail.html", context)

def chef_detail(request, chef_id):
    chef = get_object_or_404(Chef, pk=chef_id)
    open_dish_posts = chef.dishpost_set.filter(status=DishPost.OPEN)
    has_history = open_dish_posts.count() < chef.dishpost_set.count()
    context = {
        "chef": chef,
        "open_dish_posts": open_dish_posts,
        "has_history": has_history,
    }
    return render(request, "dishes/chef_detail.html", context)

def chef_history(request, chef_id):
    chef = get_object_or_404(Chef, pk=chef_id)
    past_dish_posts = chef.dishpost_set.filter(status=DishPost.COMPLETE)
    context = {
        "chef": chef,
        "past_dish_posts": past_dish_posts,
    }
    return render(request, "dishes/chef_history.html", context)

def order_follow(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    diner = order.diner
    chef = order.dish_post.chef
    if request.method == "POST":
        chef.followers.add(diner)
        chef.save()
    return redirect("orders_and_requests")

def rate_chef(request, chef_id):
    chef = get_object_or_404(Chef, pk=chef_id)
    if request.method == "POST":
        form = RateChefForm(request.POST)
        if form.is_valid():
            int_rating = request.POST["rating"]
            rating = RateChef.objects.create(chef, rating=int_rating)
        else:
            form = RateChefForm()
    return redirect(request, "dishes/rate_chef.html")

def order_feedback(request, order_id):
    context = {}
    order = get_object_or_404(Order, pk=order_id)
    if request.method == "POST":
        feedback_form = FeedbackForm(request.POST)
        rating_form = RatingForm(request.POST)
        if feedback_form.is_valid() and rating_form.is_valid():
            # Bind references
            rater = request.user
            ratee = order.dish_post.chef.user
            # Create the OrderFeedback
            feedback_data = {"order": order}
            feedback_data.update(feedback_form.cleaned_data)
            order_feedback = OrderFeedback.objects.create(**feedback_data)
            # Transfer the tip.
            tip_amt = order_feedback.tip
            if rater.balance.has_funds(tip_amt):
                rater.balance.debit(tip_amt)
                ratee.balance.credit(tip_amt)
            # Create the Rating
            rating_data = {
                "rater": rater,
                "ratee": ratee
            }
            rating_data.update(rating_form.cleaned_data)
            Rating.objects.create(**rating_data)
            # Update the order status
            order.diner_rated = True
            order.status = Order.COMPLETE
            order.save()
            if not ratee.suspensioninfo.suspended:
                check_suspend_ratee(ratee)

            check_redflag_rater(rater)
            context["feedback_submitted"] = True
            return render(request, "dishes/order_feedback.html", context)
    else:
        feedback_form = FeedbackForm()
        rating_form = RatingForm()

    chef = order.dish_post.chef
    diner = order.diner
    context["is_following"] = chef.followers.filter(id=diner.id).count()
    print(context["is_following"])
    context["feedback_form"] = feedback_form
    context["rating_form"] = rating_form
    context["has_complained"] = hasattr(order, "complaint")
    return render(request, "dishes/order_feedback.html", context)

def order_complain(request, order_id):
    context = {}
    order = get_object_or_404(Order, pk=order_id)
    if hasattr(order, "complaint"):
        return redirect("orders_and_requests")
    if request.method == "POST":
        complaint_form = ComplaintForm(request.POST)
        if complaint_form.is_valid():
            # Bind references
            complainant = request.user
            complainee = order.dish_post.chef.user
            complaint_data = {
                "complainant": complainant,
                "complainee": complainee,
                "order": order
            }
            complaint_data.update(complaint_form.cleaned_data)
            Complaint.objects.create(**complaint_data)
            check_redflag_complainant(complainant)
            return redirect("orders_and_requests")
    else:
        complaint_form = ComplaintForm()

    context["form"] = complaint_form
    return render(request, "dishes/order_complain.html", context)

def cancel_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == "POST":
        if request.user == order.diner.user:
            order.status = Order.CANCELLED
            order.save()
        return redirect("orders_and_requests")
    context = {"order": order}
    return render(request, "dishes/cancel_order.html", context)

def create_request(request):
    context = {}
    if request.method == "POST":
        dish_form = DishForm(prefix="dish", data=request.POST)
        dish_request_form = DishRequestForm(prefix="dish_request",
                                            data=request.POST)
        if dish_request_form.is_valid() and dish_form.is_valid():
            # Bind some more programmer friendly references
            diner = request.user.diner
            dish_request_form_data = dish_request_form.cleaned_data

            # Create the Dish
            # The DishForm only has the fields "name" and "description"
            # Before we can create the dish we have to collate more
            # information
            dish_data = {
                "default_price": dish_request_form_data["min_price"],
                "serving_size": dish_request_form_data["portion_size"],
                "latitude": diner.latitude,
                "longitude": diner.longitude
            }
            dish_data.update(dish_form.cleaned_data)
            dish = Dish.objects.create(**dish_data)
            classification = alchemy_language.taxonomy(text=dish.name)
            if classification["taxonomy"]:
                setattr(dish, "alchemy_label", classification['taxonomy'][0]['label'])
            dish.save()

            # Create the DishRequest
            # Similarly, collate data not contained
            # in the validated DishRequestForm.
            dish_request_data = {
                "diner": diner,
                "dish": dish,
                "latitude": diner.latitude,
                "longitude": diner.longitude
            }
            dish_request_data.update(dish_request_form_data)
            dish_request = DishRequest.objects.create(**dish_request_data)

            return redirect("orders_and_requests")
    else:
        dish_request_form = DishRequestForm(prefix="dish_request")
        dish_form = DishForm(prefix="dish")
    context["dish_request_form"] = dish_request_form
    context["dish_form"] = dish_form
    return render(request, "dishes/create_request.html", context)

def manage_open_requests(request):
    diner = request.user.diner
    open_requests = diner.dishrequest_set.filter(status=DishRequest.OPEN)
    context = {"dish_requests": open_requests}
    return render(request, "dishes/manage_requests.html", context)

def edit_request(request, dish_request_id):
    context = {}
    dish_request = get_object_or_404(DishRequest, pk=dish_request_id)
    dish = dish_request.dish
    if request.method == "POST":
        dish_request_form = DishRequestForm(prefix="dish_request",
                                            data=request.POST,
                                            instance=dish_request)
        dish_form = DishForm(prefix="dish", data=request.POST, instance=dish)
        if dish_request_form.is_valid() and dish_form.is_valid():
            dish_request_form.save()
            dish_form.save()
            return redirect("orders_and_requests")
    else:
        dish_request_form = DishRequestForm(prefix="dish_request",
                                            instance=dish_request)
        dish_form = DishForm(prefix="dish", instance=dish_request.dish)
    context["dish_request_form"] = dish_request_form
    context["dish_form"] = dish_form
    return render(request, "dishes/edit_request.html", context)

def cancel_request(request, dish_request_id):
    dish_request = get_object_or_404(DishRequest, pk=dish_request_id)
    if request.method == "POST":
        dish_request.status = DishRequest.CANCELLED
        dish_request.save()
        return redirect("orders_and_requests")
    context = {"request": dish_request}
    return render(request, "dishes/cancel_request.html", context)

def create_post(request):
    context = {}
    if request.method == "POST":
        dish_post_form = DishPostForm(prefix="dish_post",
                                      data=request.POST)
        dish_form = DishForm(prefix="dish", data=request.POST)
        if dish_post_form.is_valid() and dish_form.is_valid():
            # Bind some more programmer friendly references
            diner = request.user.diner
            chef = request.user.chef
            dish_post_form_data = dish_post_form.cleaned_data

            # Create the Dish
            # The DishForm only has the fields "name" and "description"
            # Before we can create the dish we have to collate more
            # information
            dish_data = {
                "default_price": dish_post_form_data["min_price"],
                "serving_size": dish_post_form_data["serving_size"],
            }
            dish_data.update(dish_form.cleaned_data)
            dish = Dish.objects.create(**dish_data)
            classification = alchemy_language.taxonomy(text=dish.name)
            if classification["taxonomy"]:
                setattr(dish, "alchemy_label", classification['taxonomy'][0]['label'])
            dish.save()

            # Create the DishPost
            # Similarly, collate data not contained
            # in the validated DishRequestForm.
            dish_post_data = {
                "chef": chef,
                "dish": dish,
                "latitude": diner.latitude,
                "longitude": diner.longitude
            }
            dish_post_data.update(**dish_post_form_data)
            dish_post = DishPost.objects.create(**dish_post_data)

            return redirect("orders_and_requests")
    else:
        dish_post_form = DishPostForm(prefix="dish_post")
        dish_form = DishForm(prefix="dish")

    context["dish_post_form"] = dish_post_form
    context["dish_form"] = dish_form
    return render(request, "dishes/create_post.html", context)

def manage_posts(request):
    chef = request.user.chef
    dish_posts = chef.dishpost_set
    open_dish_posts = dish_posts.filter(status=DishPost.OPEN)
    pending_dish_posts = dish_posts.filter(status=DishPost.PENDING_FEEDBACK)
    context = {
        "open_dish_posts": open_dish_posts,
        "pending_dish_posts": pending_dish_posts
    }
    return render(request, "dishes/manage_posts.html", context)

def manage_post_detail(request, dish_post_id):
    dish_post = get_object_or_404(DishPost, pk=dish_post_id)
    orders = dish_post.order_set.all()
    bids = dish_post.bid_set.filter(status=Bid.PENDING)
    context = {
        "dish_post": dish_post,
        "orders": orders,
        "Order": Order,
        "bids": bids
    }
    return render(request, "dishes/manage_post_detail.html", context)

def cancel_post(request, dish_post_id):
    dish_post = get_object_or_404(DishPost, pk=dish_post_id)
    if request.method == "POST":
        dish_post.status = DishPost.CANCELLED
        dish_post.save()
        return redirect("manage_posts")
    context = {"dish_post": dish_post}
    return render(request, "dishes/cancel_post.html", context)

def edit_post(request, dish_post_id):
    context = {}
    dish_post = get_object_or_404(DishPost, pk=dish_post_id)
    dish = dish_post.dish
    if request.method == "POST":
        dish_post_form = DishPostForm(prefix="dish_post",
                                      data=request.POST,
                                      instance=dish_post)
        dish_form = DishForm(prefix="dish", data=request.POST, instance=dish)
        if dish_post_form.is_valid() and dish_form.is_valid():
            dish_post_form.save()
            dish_form.save()
            return redirect("manage_posts")
    else:
        dish_post_form = DishPostForm(prefix="dish_post", instance=dish_post)
        dish_form = DishForm(prefix="dish", instance=dish)
    context["dish_post_form"] = dish_post_form
    context["dish_form"] = dish_form
    return render(request, "dishes/edit_post.html", context)

def follow_chef(request, chef_id):
    context = {}
    chef = get_object_or_404(Chef, pk=chef_id)
    chef.userprofile.follows.add(request.user.username)
    context["Following"] = True
    return render(request, "dishes/chef_detail.html", context)

def rate_diner(request, order_id):
    context = {}
    order = get_object_or_404(Order, pk=order_id)
    diner = order.diner
    if request.method == "POST":
        form = RatingForm(request.POST)
        if form.is_valid():
            rater = request.user
            ratee = diner.user
            # Create the Rating
            rating_data = {
                "rater": rater,
                "ratee": ratee
            }
            rating_data.update(form.cleaned_data)
            Rating.objects.create(**rating_data)
            order.chef_rated = True
            order.save()
            # Execute suspension and flagging checks
            # on the rater and ratee.
            if not ratee.suspensioninfo.suspended:
                check_suspend_ratee(ratee)
            check_redflag_rater(rater)
            return redirect("manage_posts")
    else:
        form = RatingForm()
    context["form"] = form
    return render(request, "dishes/rate_diner.html", context)

def edit_chef(request, chef_id):
    context = {}
    chef = get_object_or_404(Chef, pk=chef_id)
    if request.method == "POST":
        chef_form = ChefForm(data=request.POST, instance=chef)
        if chef_form.is_valid():
            chef_form.save()
            return redirect("chef_detail", chef_id=chef_id)
    else:
        chef_form = ChefForm(instance=chef)
    context["chef_form"] = chef_form
    return render(request, "dishes/edit_chef.html", context)

def reject_bid(request, dish_post_id, bid_id):
    if request.method == "POST":
        bid = get_object_or_404(Bid, pk=bid_id)
        bid.status = Bid.REJECTED
        bid.save()
    return redirect("manage_post_detal", dish_post_id)

def accept_bid(request, dish_post_id, bid_id):
    if request.method == "POST":
        bid = get_object_or_404(Bid, pk=bid_id)
        bid.status = Bid.ACCEPTED
        order = Order.objects.create(
            diner=bid.diner,
            dish_post=bid.dish_post,
            bid=bid,
            num_servings=bid.num_servings
        )
        bid.save()
        # Deduct the total price from the Diner's balance.
        diner_balance = bid.diner.user.balance
        if diner_balance.is_vip:
            total = decimal.Decimal(0.90) * bid.total()
        else:
            total = bid.total()
        diner_balance.debit(total)
        # Add the total price to the Chef's balance.
        chef_balance = bid.dish_post.chef.user.balance
        chef_balance.credit(bid.total())
    return redirect("manage_post_detal", dish_post_id)

def check_suspend_ratee(ratee):
    """
    Check if a user should be suspended based on their received ratings.
    """
    # Check if the ratee has 3 ratings less than 2 for
    # which the ratee has not yet been suspended.
    ratings = ratee.ratings_received
    bad_ratings = ratings.filter(rating__lte=2, struck=False)
    if bad_ratings.count() >= 3:
        # Fetch 3 of the bad ratings
        # Mark them as struck
        for bad_rating in bad_ratings.all()[:3]:
            bad_rating.struck = True
            bad_rating.save()
        # Suspend the ratee's account
        ratee.suspensioninfo.suspend()
    # Check if the ratee's average rating is out of bounds.
    elif ratings.count() >= 3:
        avg = ratings.all().aggregate(Avg("rating"))["rating__avg"]
        if avg < 2.0 or avg > 4.0:
            # Suspend the ratee's account
            ratee.suspensioninfo.suspend()

    check_force_quit(ratee)

def check_force_quit(user):
    """
    Check if a user should be forced out of the system based on their
    suspensions.
    """
    if user.suspensioninfo.count == 3:
        user.is_active = False
        user.save()

def check_redflag_rater(rater):
    """
    Check if a user should be flagged based on the ratings they give.
    """
    if check_redflag_complainant(rater):
        return
    latest_ratings = rater.ratings_made.order_by("-date")[:5]
    if not any(map(lambda r: r.struck or r.rating < 5, latest_ratings)):
        for rating in latest_ratings:
            rating.struck = True
            rating.save()
        RedFlag.objects.create(user=rater, reason=RedFlag.GENEROUS)

def check_redflag_complainant(complainant):
    """
    Check if a user should be flagged based on the complaints they have
    alleged.
    """
    lowest_ratings = complainant.ratings_made.filter(rating=1, struck=False)
    complaints = complainant.complaint_allegations.filter(struck=False)

    if lowest_ratings.count() >= 3 and complaints.count() >= 3:
        # Fetch three of the lowest ratings
        # Mark them as struck
        for low_rating in lowest_ratings.all()[:3]:
            low_rating.struck = True
            low_rating.save()

        # Fetch three of the complaints
        # Mark them as struck
        for complaint in complaints.all()[:3]:
            complaint.struck = True
            complaint.save()

        # Flag the user
        RedFlag.objects.create(user=complainant, reason=RedFlag.CRITICAL)
        return True
    else:
        return False

def suggest_dishes(request):
    context = {}
    diner_labels = []
    dish_suggestions2 = ''
    for o in Order.objects.filter(diner__user=request.user):
        diner_labels.append(o.dish_post.dish.alchemy_label)
    counted_labels = dict(Counter(diner_labels))
    suggestions = [key for key in counted_labels]
    if suggestions:
        dish_suggestions = DishPost.objects.filter(dish__alchemy_label=suggestions[0], status=DishPost.OPEN)
        if len(suggestions) > 1:
            dish_suggestions2 = DishPost.objects.filter(dish__alchemy_label=suggestions[1], status=DishPost.OPEN)
    else:
        dish_suggestions = DishPost.objects.filter(status=DishPost.OPEN)
    context["dish_suggestions"] = dish_suggestions
    context["dish_suggestions2"] = dish_suggestions2
    return render(request, "dishes/dish_suggestions.html", context)

