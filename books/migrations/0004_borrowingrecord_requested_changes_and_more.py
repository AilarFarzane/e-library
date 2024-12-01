# Generated by Django 5.1.3 on 2024-12-01 14:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0003_borrowingrecord_returned_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="borrowingrecord",
            name="requested_changes",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="borrowingrecord",
            name="user_request_status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                ],
                default="pending",
                max_length=100,
            ),
        ),
    ]
