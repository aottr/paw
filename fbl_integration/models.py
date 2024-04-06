from django.db import models
from core.models import PawUser

class FblAccount(models.Model):
    user = models.OneToOneField(PawUser, on_delete=models.CASCADE)
    badge_number = models.IntegerField()
    account_id = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    tags_secured = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=64)

    @classmethod
    def create_user(cls, username) -> PawUser:
        if not PawUser.objects.filter(username=username).exists():
            user = PawUser.objects.create(username=username)
        else:
            counter = 1
            while True:
                new_username = f"{username}_{counter}"
                if not PawUser.objects.filter(username=new_username).exists():
                    user = PawUser.objects.create(username=new_username)
                    break
                counter += 1

        user.set_unusable_password()
        user.save()
        return user
        

    def __str__(self):
        return self.user.username