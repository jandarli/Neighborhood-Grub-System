import decimal

from django import forms
from captcha.fields import CaptchaField

from accounts.models import (
    CreateAccountRequest, ChefPermissionsRequest,
    Suggestion, Complaint, RemoveSuspensionRequest
)

class CreateAccountRequestForm(forms.ModelForm):
    captcha = CaptchaField()
    class Meta:
        model = CreateAccountRequest
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "latitude",
            "longitude"
        ]
        widgets = {
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput()
        }

class TerminateAccountRequestForm(forms.Form):
    NO = 0
    YES = 1
    choice = forms.fields.ChoiceField(choices=((YES, "Yes"), (NO, "No")))

class ChefPermissionsRequestForm(forms.ModelForm):
    class Meta:
        model = ChefPermissionsRequest
        fields = [
            "first_dish_name",
            "first_dish_image",
            "second_dish_name",
            "second_dish_image",
            "third_dish_name",
            "third_dish_image",
            "video_biography"
        ]

class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ["suggestion"]

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["description"]

class DepositForm(forms.Form):
    amount = forms.DecimalField(min_value=decimal.Decimal(0.0),
                                max_value=decimal.Decimal(1000),
                                decimal_places=2)

class WithdrawalForm(forms.Form):
    amount = forms.DecimalField(min_value=decimal.Decimal(0.0),
                                max_value=decimal.Decimal(1000),
                                decimal_places=2)

class RemoveSuspensionRequestForm(forms.ModelForm):
    class Meta:
        model = RemoveSuspensionRequest
        fields = ["justification"]
