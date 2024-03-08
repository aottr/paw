from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import Group, Permission


def populate_groups(apps, schema_editor):
    user_roles = ["Client", "Supporter"]
    for name in user_roles:
        Group.objects.create(name=name)
