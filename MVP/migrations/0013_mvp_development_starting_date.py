# Generated by Django 5.0.3 on 2024-07-08 04:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("MVP", "0012_remove_mvp_cg_artist_remove_mvp_created_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="mvp",
            name="development_starting_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
