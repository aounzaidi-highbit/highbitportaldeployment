# Generated by Django 5.0.3 on 2024-05-20 10:19

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0015_evaluationformmodel_previous_month_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="employee",
            name="highbit_experience",
        ),
    ]
