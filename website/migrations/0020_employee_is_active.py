# Generated by Django 5.0.3 on 2024-06-06 09:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0019_remove_adminfeautures_enable_weightage_calculation_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="employee",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]
