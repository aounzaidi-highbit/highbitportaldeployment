# Generated by Django 5.0.3 on 2024-07-26 12:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0028_alter_employee_confirmation_date"),
    ]

    operations = [
        migrations.CreateModel(
            name="BonusEmailsHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("grade_A_bonus", models.FloatField()),
                ("grade_B_bonus", models.FloatField()),
                ("total_bonus", models.FloatField()),
                ("grade_A_employees_count", models.IntegerField(blank=True, null=True)),
                ("grade_B_employees_count", models.IntegerField(blank=True, null=True)),
                (
                    "sent_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="website.employee",
                    ),
                ),
            ],
            options={
                "verbose_name": "Bonus Email",
                "verbose_name_plural": "Bonus Emails",
            },
        ),
    ]