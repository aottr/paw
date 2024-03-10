from django.db import models
from django.contrib.auth.models import AbstractUser


class PawUser(AbstractUser):
    profile_picture = models.ImageField(
        upload_to='profile_pics/', null=True, blank=True)
    language = models.CharField(max_length=2, default='en')
    telegram_username = models.CharField(max_length=50, null=True, blank=True)
    use_darkmode = models.BooleanField(default=False)

    def __str__(self):
        return self.username
