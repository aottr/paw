# Generated by Django 5.0.3 on 2024-03-23 23:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_seed_mailtemplates"),
    ]

    operations = [
        migrations.AddField(
            model_name="pawuser",
            name="receive_email_notifications",
            field=models.BooleanField(default=True),
        ),
    ]
