# Generated by Django 4.0.6 on 2024-09-05 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MVP', '0009_mvp_created_by_alter_mvp_updated_by_shortupdate'),
    ]

    operations = [
        migrations.AddField(
            model_name='mvp',
            name='link',
            field=models.URLField(blank=True, null=True),
        ),
    ]
