# Generated by Django 5.0.3 on 2024-03-10 00:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="pawuser",
            name="use_darkmode",
            field=models.BooleanField(default=False),
        ),
    ]
