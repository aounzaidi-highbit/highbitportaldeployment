# Generated by Django 5.0.3 on 2024-07-20 06:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("MVP", "0025_alter_activity_changes"),
        ("website", "0028_alter_employee_confirmation_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="activity",
            name="created_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="website.employee",
            ),
        ),
    ]
