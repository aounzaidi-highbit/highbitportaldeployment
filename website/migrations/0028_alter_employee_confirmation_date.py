# Generated by Django 5.0.3 on 2024-07-19 07:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0027_employee_is_permanent"),
    ]

    operations = [
        migrations.AlterField(
            model_name="employee",
            name="confirmation_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
