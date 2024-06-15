# Generated by Django 5.0.3 on 2024-06-12 09:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("website", "0021_employee_mvp_role"),
    ]

    operations = [
        migrations.CreateModel(
            name="ActivityType",
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
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="MVP",
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
                ("name", models.CharField(max_length=100)),
                ("start_date", models.DateField()),
                ("is_active", models.BooleanField(default=True)),
                ("end_date", models.DateField(blank=True, null=True)),
                (
                    "current_phase",
                    models.CharField(
                        choices=[("MVP", "MVP"), ("Product", "Product")], max_length=100
                    ),
                ),
                ("created_at", models.DateField(auto_now_add=True, null=True)),
                ("updated_by", models.CharField(blank=True, max_length=50, null=True)),
                (
                    "developers",
                    models.ManyToManyField(
                        related_name="developers", to="website.employee"
                    ),
                ),
                (
                    "planners",
                    models.ManyToManyField(
                        related_name="planners", to="website.employee"
                    ),
                ),
                (
                    "team_name",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="website.teams"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Activity",
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
                ("notes", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "team_name",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="website.teams",
                    ),
                ),
                (
                    "activity_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="MVP.activitytype",
                    ),
                ),
                (
                    "mvp",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="MVP.mvp"
                    ),
                ),
            ],
        ),
    ]
