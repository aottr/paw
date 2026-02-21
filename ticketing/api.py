"""
API routes for the ticketing app.
"""
from ninja import Router, ModelSchema, Schema
from ninja.orm import create_schema
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import Ticket, Category
from core.models import PawUser
from .schemas import TicketSchema, TicketDetailSchema, CommentSchema

router = Router(tags=["tickets"])


@router.get("/", response=list[TicketSchema])
def list_tickets(request):
    """List all tickets."""
    return Ticket.get_open_tickets(request.user).order_by("priority", "-updated_at").all()

@router.get("/history", response=list[TicketSchema])
def list_tickets_history(request):
    """List all closed tickets."""
    return Ticket.get_closed_tickets(request.user).order_by("priority", "-updated_at").all()

@router.get("/{ticket_id}", response=TicketDetailSchema)
def get_ticket(request, ticket_id: int):
    """Get a specific ticket."""
    # TODO: Implement ticket retrieval logic
    return get_object_or_404(Ticket, id=ticket_id)

@router.get("/{ticket_id}/comments", response=list[CommentSchema])
def get_ticket_comments(request, ticket_id: int):
    """Get all comments for a specific ticket."""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    can_view_internal_comments = ticket.can_edit(request.user)
    if can_view_internal_comments:
        return ticket.comment_set.all()
    else:
        return ticket.comment_set.filter(is_only_for_staff=False).all()
