from django.db import models
from core.models import PawUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver


class Team(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(PawUser)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=200)
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, null=True, blank=True, help_text="If a team is selected, new tickets will automatically assigned to this team.")

    def __str__(self):
        return self.name


class Ticket(models.Model):

    class Status(models.TextChoices):
        OPEN = 'open', _('Open')
        IN_PROGRESS = 'in_progress', _('In Progress')
        CLOSED = 'closed', _('Closed')

    class Priority(models.IntegerChoices):
        LOW = 3, _("Low")
        MEDIUM = 2, _("Medium")
        HIGH = 1, _("High")

    title = models.CharField(max_length=200)
    user = models.ForeignKey(PawUser, on_delete=models.CASCADE)
    description = models.TextField()
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN)
    priority = models.PositiveSmallIntegerField(
        choices=Priority.choices, db_index=True, default=Priority.MEDIUM)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(
        PawUser, on_delete=models.CASCADE, related_name='assigned_to_user', null=True, blank=True)
    assigned_team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name='assigned_to_team', null=True, blank=True)
    follow_up_to = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name='follow_ups')

    class Meta:
        indexes = [
            models.Index(fields=["priority", "title"]),
        ]

    def close_ticket(self):
        self.status = self.Status.CLOSED
        self.save()

    def assign_to_team(self, team):
        if self.assigned_team != team and team is not None:
            self.assigned_to = None

        self.assigned_team = team
        self.save()

    def get_priority(self):
        return self.Priority(self.priority).label

    def __str__(self):
        return self.title


@receiver(post_save, sender=Ticket, dispatch_uid="team_auto_assignment")
def update_team_assignment(sender, instance, created, **kwargs):
    if not created or not instance.category or not instance.category.team:
        return

    instance.assigned_team = instance.category.team
    instance.save()


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    user = models.ForeignKey(PawUser, on_delete=models.CASCADE)
    text = models.TextField()
    is_only_for_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.ticket.status = Ticket.Status.IN_PROGRESS
        self.ticket.updated_at = timezone.now()
        self.ticket.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.ticket.title}'


class Template(models.Model):
    name = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name
