from django.db import migrations
from core.models import MailTemplate

def add_initial_templates(apps, schema_editor):
    MailTemplate.objects.create(
        event='new_user',
        name='New User Account',
        language='en',
        subject='Welcome to [Your Organization Name]!',
        content='''\
Hello {username},

Welcome to [Your Organization Name]!

Your account has been successfully created. Here are your account details:

Username: {username}
Email Address: {email}

Best regards,
[Your Organization Name]
'''
    )
        

class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_mailtemplate"),
    ]

    operations = [migrations.RunPython(add_initial_templates),]
