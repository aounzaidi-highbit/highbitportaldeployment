# Generated by Django 5.0.3 on 2024-07-22 12:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("MVP", "0028_shortupdate_created_at_shortupdate_created_by"),
        ("website", "0028_alter_employee_confirmation_date"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="shortupdate",
            options={
                "verbose_name": "Short Update",
                "verbose_name_plural": "Short Updates",
            },
        ),
        migrations.AddField(
            model_name="mvp",
            name="created_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="created_mvps",
                to="website.employee",
            ),
        ),
        migrations.AlterField(
            model_name="mvp",
            name="updated_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="updated_mvps",
                to="website.employee",
            ),
        ),
    ]
