from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.mail import send_mail


class PawUser(AbstractUser):
    profile_picture = models.ImageField(
        upload_to='profile_pics/', null=True, blank=True)
    language = models.CharField(max_length=2, default='en')
    telegram_username = models.CharField(max_length=50, null=True, blank=True)
    use_darkmode = models.BooleanField(default=False)

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
    
    def send_mail(self, to, context):
        try:
            send_mail(
                self.subject.format(**context),
                self.content.format(**context),
                settings.DEFAULT_FROM_EMAIL,
                [to],
                fail_silently=False,
            )
        except Exception as e:
            print(e)

    def __str__(self):
        return f"{self.name} - [{self.event}]"