from django.urls import path

from .views import home_view, logout_view, settings_view, register_view

urlpatterns = [
    path("", home_view, name="home"),
    path("settings", settings_view, name="settings"),
    path("register", register_view, name="register"),
    path("logout", logout_view, name="logout"),
]
