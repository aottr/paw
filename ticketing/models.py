from django.db import models
from core.models import PawUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from uuid import uuid4
from core.models import MailTemplate


def ticket_directory_path(instance, filename):
    """ file will be uploaded to MEDIA_ROOT/ticket_<id>/<filename> """
    ext = filename.split('.')[-1]
    return "attachments/ticket_{0}/{1}.{2}".format(instance.ticket.id, uuid4(), ext)


class Team(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(PawUser)
    access_non_category_tickets = models.BooleanField(default=False)
    readonly_access = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=200)
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, null=True, blank=True, help_text=_("If a team is selected, new tickets will automatically assigned to this team."))

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

    @classmethod
    def _get_tickets(cls, user) -> models.QuerySet:
        """
        For regular users with no team: return all open tickets that are created by the user
        """
        if user.is_superuser:
            return cls.objects.all()
        
        user_teams = user.team_set.all()
        if not user_teams:
            return cls.objects.filter(user=user)
        
        q = cls.objects.filter(
            models.Q(user=user) | # tickets created by user
            (models.Q(assigned_team__in=user_teams) | models.Q(assigned_to=user)) | # tickets assigned to user or user's team
            (models.Q(assigned_team=None) & models.Q(category=None)) # tickets that are not assigned and have no category (general), needs to be excluded with filter
        )

        if not any([team.access_non_category_tickets for team in user_teams]):
            return q.exclude(models.Q(assigned_team=None) & models.Q(category=None) & ~models.Q(user=user))
        return q

    @classmethod
    def get_open_tickets(cls, user) -> models.QuerySet:
        """
        For regular users with no team: return all open tickets that are created by the user
        """
        return cls._get_tickets(user).exclude(status=cls.Status.CLOSED)

    @classmethod
    def get_closed_tickets(cls, user) -> models.QuerySet:
        """
        For regular users with no team: return all closed tickets that are created by the user
        """
        return cls._get_tickets(user).filter(status=cls.Status.CLOSED)
    
    def can_open(self, user):
        if user.is_superuser:
            return True
        return self.user == user or self.assigned_to == user or self.assigned_team in user.team_set.all() or self.assigned_team is None and user.team_set.filter(access_non_category_tickets=True).exists()
    
    def can_edit(self, user):
        if user.is_superuser:
            return True
        assigned_and_write_access = self.assigned_team in user.team_set.filter(readonly_access=False) or self.assigned_to == user
        unassigned_and_write_access = self.assigned_team is None and user.team_set.filter(access_non_category_tickets=True, readonly_access=False).exists()
        print(assigned_and_write_access, unassigned_and_write_access)
        return self.can_open(user) and (assigned_and_write_access or unassigned_and_write_access)


    def close_ticket(self):
        self.status = self.Status.CLOSED
        self.save()

    def assign_to_team(self, team):
        if self.assigned_team != team and team is not None:
            self.assigned_to = None

        self.assigned_team = team
        self.save()
    
    def followed_up_by(self):
        return Ticket.objects.filter(follow_up_to=self)

    def get_priority(self):
        return self.Priority(self.priority).label

    def __str__(self):
        return self.title


@receiver(post_save, sender=Ticket, dispatch_uid="team_auto_assignment")
def update_team_assignment(sender, instance, created, **kwargs):
    if not created:
        return None
    
    if not instance.category or not instance.category.team:
        mail_template = MailTemplate.get_template('ticket_assigned')
        if not mail_template:
            return None
        #TODO send mail to all supporters
        return None
    
    # assign team to ticket
    instance.assigned_team = instance.category.team
    instance.save()

    mail_template = MailTemplate.get_template('ticket_assigned')
    if not mail_template:
        return None
    mail_template.send_mail(instance.category.team.members.values_list('email', flat=True), {
        'ticket_id': instance.id, 'ticket_title': instance.title, 'ticket_description': instance.description, 
        'ticket_priority': instance.get_priority(), 'ticket_category': instance.category.name if instance.category else _('General'),
        'ticket_creator_username': instance.user.username})



@receiver(post_save, sender=Ticket, dispatch_uid="mail_notification")
def send_mail_notification(sender, instance, created, **kwargs):
    if created and instance.user.receive_email_notifications:
        mail_template = MailTemplate.get_template('new_ticket', instance.user.language)
        if not mail_template:
            return None
        mail_template.send_mail(instance.user.email, {
            'ticket_id': instance.id, 'ticket_creator_username': instance.user.username, 'ticket_title': instance.title,
            'ticket_description': instance.description, 'ticket_category': instance.category.name if instance.category else _('General')})

@receiver(pre_save, sender=Ticket, dispatch_uid="mail_change_notification")
def send_mail_change_notification(sender, instance, update_fields=None, **kwargs):
    if not instance.user.receive_email_notifications:
        return None
    try:
        old_instance = Ticket.objects.get(id=instance.id)
    except Ticket.DoesNotExist:
        return None 
    
    if old_instance.status != instance.status:
        mail_template = MailTemplate.get_template('ticket_status_change', instance.user.language)
        if not mail_template:
            return None
        mail_template.send_mail(instance.user.email, {
            'ticket_id': instance.id, 'ticket_creator_username': instance.user.username, 'ticket_status': instance.status, 
            'ticket_status_old': old_instance.status, 'ticket_title': instance.title
        })

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

@receiver(post_save, sender=Comment, dispatch_uid="mail_comment_notification")
def send_mail_comment_notification(sender, instance, created, **kwargs):
    if created and instance.ticket.user.receive_email_notifications:
        mail_template = MailTemplate.get_template('new_comment', instance.user.language)
        if not mail_template:
            return None
        mail_template.send_mail(instance.ticket.user.email, {
            'ticket_id': instance.ticket.id, 'ticket_title': instance.ticket.title, 'ticket_creator_username': instance.user.username,
            'comment_text': instance.text})

class FileAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to=ticket_directory_path, max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{_('Attachment for')} {self.ticket.title}'


class Template(models.Model):
    name = models.CharField(max_length=200)
    content = models.TextField()
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name