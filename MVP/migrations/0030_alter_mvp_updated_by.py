# Generated by Django 5.0.3 on 2024-07-22 12:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("MVP", "0029_alter_shortupdate_options_mvp_created_by_and_more"),
        ("website", "0028_alter_employee_confirmation_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mvp",
            name="updated_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="updated_mvps",
                to="website.employee",
            ),
        ),
    ]
