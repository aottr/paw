from django.urls import path

from .views import home_view, logout_view, settings_view, register_view, login_view, google_callback_view

urlpatterns = [
    path("", home_view, name="home"),
    path("settings", settings_view, name="settings"),
    path("register", register_view, name="register"),
    path("login", login_view, name="login"),
    path("logout", logout_view, name="logout"),
    path("callback/google", google_callback_view, name="google_callback"),
]
