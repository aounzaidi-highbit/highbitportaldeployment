# Generated by Django 5.0.3 on 2024-05-27 05:17

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0017_adminfeautures_enable_weightage_calculation"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="adminfeautures",
            options={
                "verbose_name": "Admin Feature",
                "verbose_name_plural": "Admin Features",
            },
        ),
        migrations.RenameField(
            model_name="adminfeautures",
            old_name="form_enabling_date",
            new_name="form_disabling_date",
        ),
    ]
