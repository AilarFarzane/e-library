# Generated by Django 5.1.3 on 2024-11-27 13:50

import django_jalali.db.models
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="borrowingrecord",
            name="returned_date",
            field=django_jalali.db.models.jDateField(blank=True, null=True),
        ),
    ]
