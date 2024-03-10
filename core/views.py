from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .forms import UserChangeForm, RegisterForm
from .models import PawUser
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


def register_view(request):

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            PawUser.objects.create_user(
                username=form.cleaned_data.get("username"),
                email=form.cleaned_data.get("email"),
                password=form.cleaned_data.get("password")
            )
            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "core/register.html", {"form": form})


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
            request.user.use_darkmode = form.cleaned_data["use_darkmode"]
            if form.cleaned_data["profile_picture"]:
                request.user.profile_picture = form.cleaned_data["profile_picture"]
            request.user.save()
    else:
        form = UserChangeForm(initial={
            "email": request.user.email,
            "language": request.user.language,
            "telegram_username": request.user.telegram_username,
            "use_darkmode": request.user.use_darkmode,
        })

    res = render(request, "core/settings.html", {"form": form})
    if changed_user_language:
        res.set_cookie(settings.LANGUAGE_COOKIE_NAME, request.user.language)
    return res
