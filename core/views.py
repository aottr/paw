from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .forms import UserChangeForm
from django.utils import translation
from django.conf import settings
from django.contrib.auth.decorators import login_required


@login_required
def home_view(request):

    user_language = request.user.language
    translation.activate(user_language)
    res = redirect("all_tickets")
    res.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)
    return res


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def settings_view(request):
    changed_user_language = False

    if request.method == "POST":
        form = UserChangeForm(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data["language"] != request.user.language:
                translation.activate(form.cleaned_data["language"])
                changed_user_language = True

            request.user.email = form.cleaned_data["email"]
            request.user.language = form.cleaned_data["language"]
            request.user.telegram_username = form.cleaned_data["telegram_username"]
            if form.cleaned_data["profile_picture"]:
                request.user.profile_picture = form.cleaned_data["profile_picture"]
            request.user.save()
    else:
        form = UserChangeForm(initial={
            "email": request.user.email,
            "language": request.user.language,
            "telegram_username": request.user.telegram_username
        })

    res = render(request, "core/settings.html", {"form": form})
    if changed_user_language:
        res.set_cookie(settings.LANGUAGE_COOKIE_NAME, request.user.language)
    return res
