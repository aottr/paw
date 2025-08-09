from django.test import TestCase

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from ticketing.models import Ticket, Team, Category, Template, Comment

User = get_user_model()

def make_user(username="u", is_superuser=False, **kwargs):
    defaults = {"email": f"{username}@example.com", "password": "pass-1234567890"}
    defaults.update(kwargs)
    user = User.objects.create_user(username=username, **defaults)
    user.is_superuser = is_superuser
    user.save(update_fields=["is_superuser"])
    return user

def make_team(name="Team A", **kwargs):
    return Team.objects.create(name=name, **kwargs)

def make_category(name="GeneralCat", team=None):
    return Category.objects.create(name=name, team=team)

def make_ticket(user, title="T", desc="D", status=Ticket.Status.OPEN, category=None, priority=Ticket.Priority.MEDIUM, **kwargs):
    return Ticket.objects.create(
        title=title, user=user, description=desc, status=status, category=category, priority=priority, **kwargs
    )

def fake_upload(name="file.pdf", content=b"%PDF-1.4", content_type="application/pdf"):
    return SimpleUploadedFile(name=name, content=content, content_type=content_type)

class TicketListViewsTest(TestCase):
    def setUp(self):
        self.user = make_user("alice")
        self.other = make_user("bob")

    def test_requires_login(self):
        resp = self.client.get(reverse("all_tickets"))
        self.assertEqual(resp.status_code, 302)  # redirect to login

    def test_open_tickets_list_shows_user_related(self):
        self.client.force_login(self.user)
        make_ticket(self.user, title="Mine Open", status=Ticket.Status.OPEN)
        make_ticket(self.user, title="Mine Closed", status=Ticket.Status.CLOSED)
        make_ticket(self.other, title="Other Open", status=Ticket.Status.OPEN)

        resp = self.client.get(reverse("all_tickets"))
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode()
        self.assertIn("Mine Open", body)
        self.assertNotIn("Mine Closed", body)

        # Depending on your _get_tickets rules, other user’s tickets might be hidden unless team assignment applies.
        self.assertNotIn("Other Open", body)

    def test_closed_tickets_list(self):
        self.client.force_login(self.user)
        make_ticket(self.user, title="Closed 1", status=Ticket.Status.CLOSED)
        make_ticket(self.user, title="Open 1", status=Ticket.Status.OPEN)

        resp = self.client.get(reverse("tickets_history"))
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode()
        self.assertIn("Closed 1", body)
        self.assertNotIn("Open 1", body)


class TicketDetailViewTest(TestCase):
    def setUp(self):
        self.owner = make_user("owner")
        self.agent = make_user("agent")
        self.team = make_team("Support", readonly_access=False, access_non_category_tickets=True)
        self.team.members.add(self.agent)

    def test_cannot_open_without_permission(self):
        t = make_ticket(self.owner, title="Secret")
        stranger = make_user("stranger")
        self.client.force_login(stranger)
        resp = self.client.get(reverse("ticket_detail", args=[t.pk]))
        # View redirects to all_tickets when cannot open
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse("all_tickets"))

    def test_owner_can_view_and_post_comment(self):
        t = make_ticket(self.owner, title="Mine")
        self.client.force_login(self.owner)
        # GET
        resp = self.client.get(reverse("ticket_detail", args=[t.pk]))
        self.assertEqual(resp.status_code, 200)
        # POST comment
        resp = self.client.post(
            reverse("ticket_detail", args=[t.pk]),
            {"text": "Hello", "hidden_from_client": False}
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Comment.objects.filter(ticket=t).count(), 1)
        t.refresh_from_db()
        self.assertEqual(t.status, Ticket.Status.IN_PROGRESS)

    def test_assign_self_when_can_edit(self):
        # Assignable because agent is in team with write access and ticket unassigned
        t = make_ticket(self.owner, title="Assignable", assigned_team=self.team)
        self.client.force_login(self.agent)
        resp = self.client.post(reverse("ticket_detail", args=[t.pk]), {"assign_self": "1"})
        self.assertEqual(resp.status_code, 200 if resp.status_code == 200 else 302)  # allow either
        t.refresh_from_db()
        self.assertEqual(t.assigned_to, self.agent)

    def test_apply_template_prefills_comment(self):
        Template.objects.create(name="Tmpl", content="prefilled", category=None)
        t = make_ticket(self.owner, title="T")
        self.client.force_login(self.agent)
        # Grant edit permission: add team and assign ticket
        t.assigned_team = self.team
        t.save()

        resp = self.client.post(reverse("ticket_detail", args=[t.pk]), {"apply_template": "1", "template_select": Template.objects.first().pk})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "prefilled")

    def test_assign_to_team(self):
        t = make_ticket(self.owner)
        self.client.force_login(self.agent)
        resp = self.client.post(reverse("ticket_detail", args=[t.pk]), {"assign_to_team": "1", "team_select": self.team.pk})
        self.assertIn(resp.status_code, (200, 302))
        t.refresh_from_db()
        self.assertEqual(t.assigned_team, self.team)

    def test_assign_to_category(self):
        t = make_ticket(self.owner)
        cat = make_category("Cat", team=self.team)
        self.client.force_login(self.agent)
        # Give edit permission: assign agent's team
        t.assigned_team = self.team
        t.save()
        resp = self.client.post(reverse("ticket_detail", args=[t.pk]), {"assign_to_category": "1", "category_select": cat.pk})
        self.assertIn(resp.status_code, (200, 302))
        t.refresh_from_db()
        self.assertEqual(t.category, cat)

    def test_reopen_ticket(self):
        t = make_ticket(self.owner, status=Ticket.Status.CLOSED)
        # Give edit permission
        t.assigned_team = self.team
        t.save()
        self.client.force_login(self.agent)
        resp = self.client.post(reverse("ticket_detail", args=[t.pk]), {"reopen_ticket": "1"})
        self.assertIn(resp.status_code, (200, 302))
        t.refresh_from_db()
        self.assertEqual(t.status, Ticket.Status.IN_PROGRESS)

class TicketCreateViewTest(TestCase):
    def setUp(self):
        self.user = make_user("creator")

    def test_requires_login(self):
        resp = self.client.get(reverse("create_ticket"))
        self.assertEqual(resp.status_code, 302)

    def test_create_ticket_basic(self):
        self.client.force_login(self.user)
        resp = self.client.post(reverse("create_ticket"), {
            "title": "Issue",
            "description": "Something broken",
            "category": "",  # General
            "follow_up_to": "",  # No Follow-up
        })
        self.assertEqual(resp.status_code, 302)
        t = Ticket.objects.get()
        self.assertEqual(t.title, "Issue")
        self.assertEqual(t.user, self.user)

    def test_create_with_attachments(self):
        self.client.force_login(self.user)
        f1 = fake_upload("a.pdf", b"%PDF-1.4", "application/pdf")
        resp = self.client.post(reverse("create_ticket"), {
            "title": "With files",
            "description": "desc",
            "category": "",
            "follow_up_to": "",
            "attachments": [f1],
        })
        self.assertEqual(resp.status_code, 302)
        t = Ticket.objects.get(title="With files")
        self.assertEqual(t.fileattachment_set.count(), 1)

    def test_follow_up_queryset_only_closed_by_user(self):
        self.client.force_login(self.user)
        closed = make_ticket(self.user, title="Closed", status=Ticket.Status.CLOSED)
        other_open = make_ticket(self.user, title="Open", status=Ticket.Status.OPEN)
        resp = self.client.get(reverse("create_ticket"))
        self.assertEqual(resp.status_code, 200)
        form = resp.context["form"]
        qs = form.fields["follow_up_to"].queryset
        self.assertIn(closed, qs)
        self.assertNotIn(other_open, qs)

# class DashboardViewTest(TestCase):
#     def setUp(self):
#         self.user = make_user("viewer")
#         self.client.force_login(self.user)

#     def test_groups_by_status(self):
#         make_ticket(self.user, title="O1", status=Ticket.Status.OPEN)
#         make_ticket(self.user, title="P1", status=Ticket.Status.IN_PROGRESS)
#         make_ticket(self.user, title="C1", status=Ticket.Status.CLOSED)

#         resp = self.client.get(reverse("dashboard"))
#         self.assertEqual(resp.status_code, 200)
#         ctx = resp.context
#         self.assertEqual(ctx["open_tickets"].count(), 1)
#         self.assertEqual(ctx["in_progress_tickets"].count(), 1)
#         self.assertEqual(ctx["closed_tickets"].count(), 1)

class TicketAccessTest(TestCase):
    def setUp(self):
        self.owner = make_user("owner")
        self.agent = make_user("agent")
        self.viewer = make_user("viewer")
        self.team_rw = make_team("RW", access_non_category_tickets=True, readonly_access=False)
        self.team_ro = make_team("RO", access_non_category_tickets=True, readonly_access=True)
        self.team_rw.members.add(self.agent)
        self.team_ro.members.add(self.viewer)

    def test_can_open_rules(self):
        t_general = make_ticket(self.owner, category=None, assigned_team=None)
        t_assigned_team = make_ticket(self.owner, category=None, assigned_team=self.team_rw)
        t_assigned_user = make_ticket(self.owner, category=None, assigned_to=self.agent)

        self.assertTrue(t_general.can_open(self.agent))  # has access_non_category_tickets via team_rw
        self.assertTrue(t_assigned_team.can_open(self.agent))
        self.assertTrue(t_assigned_user.can_open(self.agent))

        stranger = make_user("stranger")
        self.assertFalse(t_assigned_team.can_open(stranger))

    def test_can_edit_requires_write_access(self):
        t = make_ticket(self.owner, assigned_team=self.team_rw)
        self.assertTrue(t.can_edit(self.agent))  # RW team member

        t2 = make_ticket(self.owner, assigned_team=self.team_ro)
        self.assertFalse(t2.can_edit(self.viewer))  # RO team member

        # Unassigned general with access_non_category_tickets but viewer is read-only, so cannot edit
        t3 = make_ticket(self.owner, assigned_team=None, category=None)
        self.assertFalse(t3.can_edit(self.viewer))