from django.urls import path

from .views import fbl_authentication_start, fbl_authentication_get_code, complete_registration

urlpatterns = [
    path("auth_start", fbl_authentication_start, name="fbl_auth_start"),
    path("auth_get_code", fbl_authentication_get_code, name="fbl_auth_get_code"),
    path("complete_registration", complete_registration, name="fbl_complete_registration"),
]
