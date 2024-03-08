from django.urls import path

from .views import show_ticket, show_tickets, create_ticket, dashboard, show_tickets_history

urlpatterns = [
    path("tickets/<int:ticket_id>", show_ticket, name="ticket_detail"),
    path("tickets/new", create_ticket, name="create_ticket"),
    path("tickets", show_tickets, name="all_tickets"),
    path("tickets/history", show_tickets_history, name="tickets_history"),
    path("dashboard", dashboard, name="dashboard"),
]
