# Generated by Django 5.0.3 on 2024-06-12 09:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("MVP", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mvp",
            name="updated_by",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
