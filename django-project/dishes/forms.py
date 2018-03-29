from django import forms
from dishes.models import (
    Dish, DishRequest, DishPost, Chef,
    OrderFeedback, RateChef, RateDiner,
    Rating, Bid, Offer
)


class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = [
            "name",
            "description"
        ]

class DishRequestForm(forms.ModelForm):
    class Meta:
        model = DishRequest
        fields = [
            "portion_size",
            "num_servings",
            "min_price",
            "meal_time"
        ]

class DishPostForm(forms.ModelForm):
    class Meta:
        model = DishPost
        fields = [
            "max_servings",
            "serving_size",
            "min_price",
            "last_call",
            "meal_time",
            "latitude",
            "longitude"
        ]
        widgets = {
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput()
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = OrderFeedback
        fields = [
            "feedback",
            "tip"
        ]

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ["rating"]

class RateChefForm(forms.ModelForm):
    class Meta:
        model = RateChef
        fields =[
            "rating"
        ]

class RateDinerForm(forms.ModelForm):
    class Meta:
        model = RateDiner
        fields =[
            "rating"
        ]

class ChefForm(forms.ModelForm):
    class Meta:
        model = Chef
        fields = [
            "name",
            "blurb",
            "experience",
        ]

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = [
            "num_servings",
            "price"
        ]

class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ["price"]
