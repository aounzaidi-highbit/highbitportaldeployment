# Generated by Django 4.0.6 on 2024-07-18 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MVP', '0006_remove_mvp_is_active_activity_created_by_mvp_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='mvp',
            name='first_completion_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
