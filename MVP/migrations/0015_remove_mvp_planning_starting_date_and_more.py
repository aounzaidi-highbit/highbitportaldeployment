# Generated by Django 5.0.3 on 2024-07-09 12:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("MVP", "0014_mvp_planning_starting_date"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="mvp",
            name="planning_starting_date",
        ),
        migrations.AlterField(
            model_name="mvp",
            name="current_phase",
            field=models.CharField(
                choices=[
                    ("MVP", "MVP"),
                    ("Product", "Product"),
                    ("Archive", "Archive"),
                ],
                max_length=100,
            ),
        ),
    ]
