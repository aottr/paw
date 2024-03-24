from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Ticket, Template
from django.db.models import Q
from .forms import CommentForm, TicketForm, TemplateForm, TeamAssignmentForm, CategoryAssignmentForm


@login_required
def show_tickets(request):
    tickets = Ticket.get_open_tickets(request.user).order_by("priority", "-updated_at")
    return render(request, "ticketing/tickets.html", {"tickets": tickets})


@login_required
def show_tickets_history(request):
    if request.user.is_staff:
        tickets = Ticket.objects.filter(
            status=Ticket.Status.CLOSED).order_by("priority", "-created_at")
        print(tickets)
    else:
        tickets = Ticket.objects.filter(
            user=request.user).order_by("-created_at")
    return render(request, "ticketing/tickets_history.html", {"tickets": tickets})


@login_required
def show_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    can_edit = ticket.can_edit(request.user)
    # comment_templates = Template.objects.filter(category=ticket.category)

    if not ticket.can_open(request.user):
        return redirect("all_tickets")

    form, template_form, team_assignment_form, category_assignment_form = CommentForm(
    ), TemplateForm(), TeamAssignmentForm(), CategoryAssignmentForm()

    if request.method == "POST":
        if 'apply_template' in request.POST and can_edit:
            template_form = TemplateForm(request.POST)
            if template_form.is_valid():
                template = template_form.cleaned_data["template_select"]
                form = CommentForm(initial={"text": template.content})
        elif 'assign_to_team' in request.POST and can_edit:
            team_assignment_form = TeamAssignmentForm(request.POST)
            if team_assignment_form.is_valid():
                ticket.assign_to_team(
                    team_assignment_form.cleaned_data["team_select"])
        elif 'assign_to_category' in request.POST and can_edit:
            category_assignment_form = CategoryAssignmentForm(request.POST)
            if category_assignment_form.is_valid():
                ticket.category = category_assignment_form.cleaned_data["category_select"]
                ticket.save()
        elif 'assign_self' in request.POST and can_edit:
            ticket.assigned_to = request.user
            ticket.save()
        elif 'reopen_ticket' in request.POST and can_edit:
            ticket.status = Ticket.Status.IN_PROGRESS
            ticket.save()
        else:
            form = CommentForm(request.POST, request.FILES)
            if form.is_valid():
                ticket.comment_set.create(
                    user=request.user, ticket=ticket,
                    text=form.cleaned_data["text"], is_only_for_staff=form.cleaned_data["hidden_from_client"]
                )
                # Add attachments
                if form.cleaned_data["attachments"]:
                    for file in form.cleaned_data["attachments"]:
                        ticket.fileattachment_set.create(file=file)

                if 'close' in request.POST and can_edit:
                    ticket.close_ticket()
                return redirect("ticket_detail", ticket_id=ticket.id)

    comments = ticket.comment_set.all()
    context = {
        "ticket": ticket, "comments": comments, "attachments": [attachment.file for attachment in ticket.fileattachment_set.all()],
        "form": form, "template_form": template_form,
        "team_assignment_form": team_assignment_form, "category_assignment_form": category_assignment_form,
        "can_edit": can_edit
    }
    return render(request, "ticketing/ticket_detail.html", context)


@login_required
def create_ticket(request):

    has_closed_tickets = Ticket.objects.filter(
        user=request.user, status=Ticket.Status.CLOSED).exists()

    if request.method == "POST":
        form = TicketForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()

            # Add attachments
            if form.cleaned_data["attachments"]:
                for file in form.cleaned_data["attachments"]:
                    ticket.fileattachment_set.create(file=file)

            return redirect("ticket_detail", ticket_id=ticket.id)
    else:
        form = TicketForm(request.user)
    return render(request, "ticketing/create_ticket.html", {"form": form, "has_closed_tickets": has_closed_tickets})


@login_required
def dashboard(request):

    tickets = Ticket.objects.all().order_by("-created_at")
    open_tickets = tickets.filter(status=Ticket.Status.OPEN)
    in_progress_tickets = tickets.filter(status=Ticket.Status.IN_PROGRESS)
    closed_tickets = tickets.filter(status=Ticket.Status.CLOSED)
    return render(request, "ticketing/dashboard.html", {"tickets": tickets, "open_tickets": open_tickets, "in_progress_tickets": in_progress_tickets, "closed_tickets": closed_tickets})
