from django.shortcuts import render, redirect

from accounts.forms import (
    ChefPermissionsRequestForm, CreateAccountRequestForm,
    TerminateAccountRequestForm, SuggestionForm, DepositForm,
    WithdrawalForm, RemoveSuspensionRequestForm
)

from accounts.models import *
from dishes.models import *

def signup(request):
    if request.method == "POST":
        form = CreateAccountRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = CreateAccountRequestForm()

    context = {"form": form}
    return render(request, "accounts/signup.html", context)

def account(request):
    is_chef = hasattr(request.user, "chef")
    user = request.user
    requests = user.chefpermissionsrequest_set
    pending_requests = requests.filter(status=ChefPermissionsRequest.PENDING)
    context = {
        "is_chef": is_chef,
        "pending_requests": pending_requests.count()
    }
    return render(request, "accounts/account.html", context)

def terminate(request):
    context = {}
    if request.method == "POST":
        form = TerminateAccountRequestForm(request.POST)
        if form.is_valid():
            choice = int(form.cleaned_data["choice"])
            if choice == TerminateAccountRequestForm.YES:
                try:
                    TerminateAccountRequest.objects.get(user=request.user)
                    return redirect("account")
                except TerminateAccountRequest.DoesNotExist:
                    TerminateAccountRequest.objects.create(user=request.user)
                    context["request_confirmed"] = True
            else:
                return redirect("account")
    else:
        form = TerminateAccountRequestForm()
    context["form"] = form
    return render(request, "accounts/user_confirm_terminate.html", context)

def request_chef_permissions(request):
    context = {}
    if request.method == "POST":
        form = ChefPermissionsRequestForm(request.POST, request.FILES)
        if form.is_valid():
            ChefPermissionsRequest.objects.create(user=request.user,
                                                  **form.cleaned_data)
            context["request_confirmed"] = True
    else:
        form = ChefPermissionsRequestForm()

    context["form"] = form
    return render(request, "accounts/request-chef-permissions.html", context)

def suggestion(request):
    context = {}
    if request.method == "POST":
        form = SuggestionForm(request.POST)
        if form.is_valid():
            form.save()
            context["suggestion_received"] = True
    else:
        form = SuggestionForm()

    context["form"] = form
    return render(request, "accounts/suggestion.html", context)

def deposit(request):
    context = {}
    if request.method == "POST":
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            request.user.balance.credit(amount)
            return redirect("account")
    else:
        form = DepositForm()
    context["form"] = form
    return render(request, "accounts/deposit.html", context)

def withdraw(request):
    overdrawn = False
    context = {}
    user = request.user
    if request.method == "POST":
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            if amount <= user.balance.amount:
                user.balance.debit(amount)
                return redirect("account")
            else:
                overdrawn = True
    else:
        form = WithdrawalForm()

    context["overdrawn"] = overdrawn
    context["form"] = form
    return render(request, "accounts/withdraw.html", context)

def suspended(request):
    context = {"RemoveSuspensionRequest": RemoveSuspensionRequest}
    user = request.user
    if request.method == "POST":
        form = RemoveSuspensionRequestForm(request.POST)
        if form.is_valid():
            data = {"user": user}
            data.update(form.cleaned_data)
            RemoveSuspensionRequest.objects.create(**data)
    else:
        form = RemoveSuspensionRequestForm()
    context["form"] = form
    if RemoveSuspensionRequest.objects.filter(
        status=RemoveSuspensionRequest.PENDING,
        user=user):
        context["pending_request"] = True
    else:
        context["pending_request"] = False
    return render(request, "accounts/suspended.html", context)
