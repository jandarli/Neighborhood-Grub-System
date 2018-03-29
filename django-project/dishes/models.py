import decimal

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Diner(models.Model):
    """
    Django model class representing a Diner.

    Attributes:

    user:
        The User account associated with this Diner instance.

    latitude:
        The latitude coordinate of this user's default location.

    longitude:
        The longitude coordinate of this user's default location.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9,
                                   decimal_places=6,
                                   default=decimal.Decimal(0.0))
    longitude = models.DecimalField(max_digits=9,
                                    decimal_places=6,
                                    default=decimal.Decimal(0.0))


class Chef(models.Model):
    """
    Django model class representing a Chef.

    Attributes:

    user:
        The User account associated with this Chef instance.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    blurb = models.TextField("Blurb")
    experience = models.TextField("Experience")
    followers = models.ManyToManyField(Diner, related_name="followees")

    def count_followers(self):
        return self.followers.all().count()

class CuisineTag(models.Model):
    """
    Django model class representing a cuisine tag.
    """
    name = models.CharField(max_length=64, unique=True)

class Dish(models.Model):
    """
    Django model class representing a dish in NGS.
    """

    """ The default price of the dish.

    Since the same Dish instance may be used to create multiple Dish Requests
    and Dish Posts we must decouple the price information from the template.
    Otherwise one could not change the price of one Request without changing
    all the others. Also, price history information would also need to be
    preserved separately.

    max_digits=4 and decimal_places=2 limits the price to no more than $99.99.
    """
    name = models.CharField(max_length=128)
    description = models.TextField("Dish Description")
    alchemy_label = models.TextField()
    default_price = models.DecimalField(max_digits=4,
                                        decimal_places=2,
                                        null=True)
    cuisine_tags = models.ManyToManyField(CuisineTag)
    serving_size = models.DecimalField(max_digits=3,
                                       decimal_places=1,
                                       default=decimal.Decimal(1.0))

    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=decimal.Decimal(0.0))
    longitude= models.DecimalField(max_digits=9, decimal_places=6, default=decimal.Decimal(0.0))



class DishPost(models.Model):
    """
    Django model class representing a Dish posted by a Chef for a Diner to
    order.

    Attributes:

    chef:
        Foreign Key field referencing the Chef who has created this Dish
        Post.

    diners:
        Many to Many field mapping DishPosts to Diners.

    dish:
        Foreign key field referencing the Dish the Chef is going to cook.

    min_price:
        Decimal field that stores the price of one serving of this Dish.

    max_servings:
        Integer field that indicates the maximum servings of this Dish the Chef
        is willing to cook.

    serving_size:
        Decimal field that indicates the size of one serving in NGS containers.

    last_call:
        Date time field that indicates the time past which the Chef will not
        accept further orders.

    meal_time:
        Date time field that indicates the approximate time the Dish is to be
        served. The Chef and Diner should coordinate the exchange of food at or
        around this time.

    status:
        Integer field that indicates the status of the order. The status
        descriptions are below.

        Open:
            At least 1 serving of the Dish Post is still available so a Diner
            may still order the Dish.
        Complete:
            The Dish has been served and the Chef has been paid.
    """
    chef = models.ForeignKey(Chef, on_delete=models.SET_NULL, null=True)
    max_servings = models.IntegerField(default=1)
    dish = models.ForeignKey(Dish, on_delete=models.PROTECT)
    min_price = models.DecimalField("Minimum Price", max_digits=4, decimal_places=2)
    serving_size = models.DecimalField(max_digits=3, decimal_places=1)
    last_call = models.DateTimeField("Last Call")
    meal_time = models.DateTimeField("Meal Time")
    latitude = models.DecimalField(max_digits = 9, decimal_places = 6, default=decimal.Decimal(0.0))
    longitude= models.DecimalField(max_digits = 9, decimal_places = 6, default=decimal.Decimal(0.0))

    OPEN, PENDING_FEEDBACK, CANCELLED, COMPLETE = range(4)

    STATUS_CHOICES = (
        (OPEN, "Open"),
        (PENDING_FEEDBACK, "Pending Feedback"),
        (CANCELLED, "Cancelled"),
        (COMPLETE, "Complete")
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=OPEN)

    def servings_ordered(self):
        acc = 0
        for order in self.order_set.all():
            acc += order.num_servings
        return acc

    def available_servings(self):
        if self.status == DishPost.COMPLETE:
            return 0
        else:
            return self.max_servings - self.servings_ordered()


class DishRequest(models.Model):
    """
    Django model class representing a dish posted by a Diner for a Chef to
    fill.

    Attributes:

    diner:
        The Diner creating the dish request.

    dish:
        Foreign key field referencing the Dish the Diner is requesting.

    portion_size:
        Decimal field that indicates the requested portion size of one serving
        of the dish.

    num_servings:
        Integer field that indicates the number of servings the Diner is
        requesting the Chef to cook.

    min_price:
        Decimal field that stores the price of one serving of this Dish.

    meal_time:
        Date time field that indicates the approximate time the Dish is to be
        served. The Chef and Diner should coordinate the exchange of food at or
        around this time.

    status:
        Integer field that indicates the status of the order. The status
        descriptions are below.

        Open:
            No Chef has yet agreed to fulfill the request and the request is still
            standing.
        Closed:
            A Chef has agreed to fulfill the request, but the dish has not yet
            been served.
        Cancelled:
            The Diner has cancelled this Dish Request.
        Complete:
            The Dish has been served and the Chef has been paid.
    """
    diner = models.ForeignKey(Diner, on_delete=models.SET_NULL, null=True)
    dish = models.ForeignKey(Dish, on_delete=models.PROTECT)
    portion_size = models.DecimalField(max_digits=3, decimal_places=1)
    num_servings = models.IntegerField(default=1)
    min_price = models.DecimalField("Minimum Price", max_digits=4, decimal_places=2)
    meal_time = models.DateTimeField("Meal Time")

    latitude = models.DecimalField(max_digits = 9, decimal_places = 6,default=decimal.Decimal(0.0))
    longitude= models.DecimalField(max_digits = 9, decimal_places = 6,default=decimal.Decimal(0.0))

    OPEN, ACCEPTED, CANCELLED, COMPLETE = range(4)

    STATUS_CHOICES = (
        (OPEN, "Open"),
        (ACCEPTED, "Accepted"),
        (CANCELLED, "Cancelled"),
        (COMPLETE, "Complete")
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=OPEN)

    def total(self):
        return self.min_price * self.num_servings

class Offer(models.Model):
    """
    Django model class representing an offer by a Chef on a diner's
    DishRequest.
    """
    chef = models.ForeignKey(Chef, on_delete=models.SET_NULL, null=True)
    dish_request = models.ForeignKey(DishRequest,
                                     on_delete=models.SET_NULL,
                                     null=True)
    price = models.DecimalField(max_digits=4, decimal_places=2)

    PENDING, ACCEPTED, REJECTED = range(3)

    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected")
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)

    def total(self):
        return self.dish_request.num_servings * self.price

class Bid(models.Model):
    """
    Django model class representing a bid on a dish post.
    """
    diner = models.ForeignKey(Diner, on_delete=models.SET_NULL, null=True)
    dish_post = models.ForeignKey(DishPost,
                                  on_delete=models.SET_NULL,
                                  null=True)
    num_servings = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=4, decimal_places=2)

    PENDING, ACCEPTED, REJECTED = range(3)

    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected")
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)

    def total(self):
        return self.num_servings * self.price


class Order(models.Model):
    """
    Django model class representing an Order made by a Diner for a Posted Dish.
    The Order model is used to capture the mapping of Diners to Dish Posts
    and how many servings of the of the Dish Post the Diner wishes to have.

    Attributes:

    diner:
        The Diner placing the order.

    dish_post:
        The Dish Post the diner is ordering.

    bid:
        The bid that was placed to create this order.

    num_servings:
        The number of servings of the Dish the Diner wishes to order.

    diner_rated:
        Indicates whether the diner has rated the chef for this order.

    chef_rated:
        Indicates whether the chef has rated the diner for this order.

    status:
        The status of this order. Status descriptions are given below.

        Open:
            This order is currently open and waiting to be filled.

        Cancelled:
            This order has been cancelled.

        Completed:
            This order has been completed.
    """
    diner = models.ForeignKey(Diner, on_delete=models.SET_NULL, null=True)
    dish_post = models.ForeignKey(DishPost, on_delete=models.PROTECT)
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE)
    num_servings = models.IntegerField(default=1)
    diner_rated = models.BooleanField(default=False)
    chef_rated = models.BooleanField(default=False)

    OPEN, PENDING_FEEDBACK, CANCELLED, COMPLETE = range(4)

    STATUS_CHOICES = (
        (OPEN, "Open"),
        (PENDING_FEEDBACK, "Pending Feedback"),
        (CANCELLED, "Cancelled"),
        (COMPLETE, "Complete")
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=OPEN)

    def total(self):
        return self.bid.total()

class OrderFeedback(models.Model):
    """
    Django model class representing feedback from a diner about an
    order that has been placed and received (i.e. completed).

    Attributes:

    order:
        The order this feedback is about.

    date:
        The date and time the feedback was received.

    feedback:
        The feedback from the diner about the order.

    tip:
        The amount of tip the Diner has given with this order.
    """
    order = models.OneToOneField(Order, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField()
    tip = models.DecimalField(max_digits=4,
                              decimal_places=2,
                              default=decimal.Decimal(0.0))


    def __unicode__(self):
        return self.title

class RateChef(models.Model):
    """
    Django model class representing the rating between 1 and 5 of
    chef by a diner.

    Attributes:

    chef:
        The chef being rated

    rating: number between 1 and 5
    """

    chef = models.ForeignKey(Chef, on_delete=models.SET_NULL, null=True)
    rating = models.IntegerField(validators=[MinValueValidator(1),
                                             MaxValueValidator(5)])

    def average_rating(self):
        curr_sum = 0
        for rating in RateChef.objects.all():
            curr_sum += rating.rating
        return curr_sum/len(RateChef.objects.all)


class RateDiner(models.Model):
    """
    Django model class representing the rating of diner by a chef
    with a score between 1 and 5

    Attributes:

    diner:
     The diner being rated

    rating: between 1 and 5
    """
    diner = models.ForeignKey(Chef, on_delete=models.SET_NULL, null=True)
    rating = models.IntegerField(validators=[MinValueValidator(1),
                                             MaxValueValidator(5)])

    def average_rating(self):
        curr_sum = 0
        for rating in RateDiner.objects.all():
            curr_sum += rating.rating
        return curr_sum/len(RateDiner.objects.all)

class Rating(models.Model):
    """
    Django model class representing a rating of a user.

    Attributes:

    rater:
        The user submitting the rating.

    ratee:
        The user being rated.

    rating:
        The score given the ratee by the rater in the range 1 to 5.

    struck:
        Whether the ratee has been suspended as a result of this rating.

    date:
        The date and time when the rating was submitted.
    """
    rater = models.ForeignKey(User,
                              on_delete=models.SET_NULL,
                              null=True,
                              related_name="ratings_made")
    ratee = models.ForeignKey(User,
                              on_delete=models.SET_NULL,
                              null=True,
                              related_name="ratings_received")
    rating = models.IntegerField(validators=[MinValueValidator(1),
                                             MaxValueValidator(5)])
    struck = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)




