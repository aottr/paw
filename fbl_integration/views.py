from django.shortcuts import render, redirect
from django.contrib.auth import login
from datetime import datetime
from .forms import FblAuthForm, FblAuthCodeForm, RegistrationCompletionForm
from .utils import fbl_auth_request_code, fbl_auth_validate_code, fbl_auth_get_account, get_or_create_account

def fbl_authentication_start(request):
    print('fbl auth started')
    auth_form = FblAuthForm(request.POST or None)
    if request.method == "POST":
        if auth_form.is_valid():

            valid_info = fbl_auth_request_code(
                badge_number=auth_form.cleaned_data["badge_number"],
                dob=auth_form.cleaned_data["dob"]
            )
            if valid_info:
                code_form = FblAuthCodeForm(initial={
                **auth_form.cleaned_data,
                "dob": datetime.strptime(auth_form.cleaned_data["dob"], "%Y-%m-%d").strftime("%d/%m/%Y"),
                })
            
                return render(request, "fbl_auth_get_code.html", {"get_code_form": code_form})
            
            auth_form.add_error(None, "Invalid badge number or date of birth")

    return render(request, "fbl_auth_start.html", {"form": auth_form})


def fbl_authentication_get_code(request):
    code_form = FblAuthCodeForm(request.POST or None)
    if request.method == "POST":
        if code_form.is_valid():
            access_token = fbl_auth_validate_code(
                badge_number=code_form.cleaned_data["badge_number"],
                dob=code_form.cleaned_data["dob"],
                validation_code=code_form.cleaned_data["validation_code"]
            )
            if access_token:
                account_info = fbl_auth_get_account(access_token)
                fbl_account = get_or_create_account(account_info)
                
                login(request=request, user=fbl_account.user)

                if not fbl_account.user.email:
                    return redirect("fbl_complete_registration")
                else:
                    return redirect("all_tickets")

            code_form.add_error(None, "Invalid validation code")


    return render(request, "fbl_auth_get_code.html", {"get_code_form": code_form})

def complete_registration(request):
    form = RegistrationCompletionForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            request.user.email = form.cleaned_data["email"]
            request.user.save()
            return redirect("all_tickets")
    return render(request, "complete_registration.html", {"form": form})