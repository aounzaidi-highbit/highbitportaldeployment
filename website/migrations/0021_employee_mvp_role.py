# Generated by Django 5.0.3 on 2024-06-07 10:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0020_employee_is_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="mvp_role",
            field=models.CharField(
                choices=[("Planner", "Planner"), ("Developer", "Developer")],
                max_length=20,
                null=True,
            ),
        ),
    ]
