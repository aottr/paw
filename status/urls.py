from django.urls import path

from .views import IncidentListView

urlpatterns = [
    path("", IncidentListView.as_view(), name="incident-list"),
]
