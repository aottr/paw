from django.urls import path

from .views import fbl_authentication_start, fbl_authentication_get_code

urlpatterns = [
    path("auth_start", fbl_authentication_start, name="fbl-auth-start"),
    path("auth_get_code", fbl_authentication_get_code, name="fbl-auth-get-code")
]
