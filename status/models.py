from django.db import models


class Incident(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    public = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.title
