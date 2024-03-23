from django.db import migrations
from core.models import MailTemplate

def add_initial_templates(apps, schema_editor):
    MailTemplate.objects.create(
        event='ticket_status_change',
        name='Ticket Status Change',
        language='en',
        subject='Your ticket status has changed',
        content='''\
Hello {ticket_creator_username},

This is to inform you that the status of your ticket #{ticket_id} {ticket_title} has been changed from "{ticket_status_old} to "{ticket_status}".

Thank you for your patience.

Best regards,
[Your Organization Name]
'''
    )

    MailTemplate.objects.create(
        event='new_ticket',
        name='New Ticket',
        language='en',
        subject='Your ticket has been created successfully',
        content='''\
Dear {ticket_creator_username},

We're writing to inform you that your ticket #{ticket_id} has been created successfully.

Details:
Title: {ticket_title}
Category: {ticket_category}
Description: 
{ticket_description}

Our team will review your ticket and respond as soon as possible. You can track the status of your ticket by logging into your account.

Thank you for reaching out to us.

Best regards,
[Your Organization Name]
'''
    )

    MailTemplate.objects.create(
        event='ticket_assigned',
        name='Ticket Assignment',
        language='en',
        subject='A new ticket has been assigned to your team',
        content='''\
Hello Team,

A new ticket has been created with the following details:

Ticket ID: #{ticket_id}
Title: {ticket_title}
Priority: {ticket_priority}
Category: {ticket_category}
Created By: {ticket_creator_username}
Description: 
{ticket_description}

Please review the ticket and take appropriate action.

Thank you for your attention.

Best regards,
[Your Organization Name]
'''
    )
        


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_mailtemplate"),
    ]

    operations = [migrations.RunPython(add_initial_templates),]
