# Generated by Django 5.0.3 on 2024-07-18 11:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0025_alter_employee_mvp_role"),
    ]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="grade",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
