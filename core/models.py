from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from django.core.mail import send_mail


class PawUser(AbstractUser):
    profile_picture = models.ImageField(
        upload_to='profile_pics/', null=True, blank=True)
    language = models.CharField(max_length=2, default='en')
    telegram_username = models.CharField(max_length=50, null=True, blank=True)
    use_darkmode = models.BooleanField(default=False)
    receive_email_notifications = models.BooleanField(default=True)

    def __str__(self):
        return self.username


class GoogleSSOUser(models.Model):
    paw_user = models.OneToOneField(
        PawUser, on_delete=models.CASCADE, primary_key=True)
    google_id = models.CharField(max_length=255)

    def __str__(self):
        return self.paw_user.username

    class Meta:
        db_table = "google_sso_user"
        verbose_name = _("Google SSO User")

class MailTemplate(models.Model):
    event = models.CharField(max_length=100)
    language = models.CharField(max_length=2, default='en', choices=settings.LANGUAGES)
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    content = models.TextField()

    @classmethod
    def get_template(cls, event, language='en'):
        template = cls.objects.filter(event=event, language=language).first()
        if not template:
            template = cls.objects.filter(event=event, language='en').first()
        return template
    
    def send_mail(self, to_list: list[str], context):
        try:
            send_mail(
                self.subject.format(**context),
                self.content.format(**context),
                settings.DEFAULT_FROM_EMAIL,
                to_list,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending email with type {type(e)}: {e}")

    def __str__(self):
        return f"{self.name} - [{self.event}]"

@receiver(post_save, sender=PawUser, dispatch_uid="new_user_notification")
def new_user_notification(sender, instance, created, **kwargs):
    if not created or not instance.email:
        return None
    
    mail_template = MailTemplate.get_template('new_user', instance.language)
    if not mail_template:
        return None
    mail_template.send_mail([instance.email], {
        'username': instance.username, 'email': instance.email })