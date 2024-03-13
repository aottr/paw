from django.shortcuts import render
from django.views.generic import ListView
from .models import Incident


class IncidentListView(ListView):
    model = Incident

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["existing_incidents"] = Incident.objects.filter(public=True, resolved=False).exists()
        return context

    def get_queryset(self):
        return Incident.objects.filter(public=True).order_by('resolved')