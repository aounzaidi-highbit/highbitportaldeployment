# Generated by Django 5.0.3 on 2024-06-24 05:50

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("MVP", "0007_mvp_game_plan_alter_mvp_name"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="mvp",
            name="game_plan",
        ),
    ]
