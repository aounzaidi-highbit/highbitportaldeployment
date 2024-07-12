# Generated by Django 4.0.6 on 2024-07-10 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MVP', '0004_mvp_development_starting_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mvp',
            name='planning_starting_date',
        ),
        migrations.AddField(
            model_name='mvp',
            name='is_archived',
            field=models.BooleanField(default=False),
        ),
    ]
