# Generated by Django 5.0.3 on 2024-06-15 12:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("MVP", "0006_alter_activity_options_alter_activitytype_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="mvp",
            name="game_plan",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="mvp",
            name="name",
            field=models.CharField(max_length=100),
        ),
    ]
