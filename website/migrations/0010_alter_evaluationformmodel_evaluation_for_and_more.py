# Generated by Django 5.0.3 on 2024-05-13 11:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0009_employee_joining_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="evaluationformmodel",
            name="evaluation_for",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="evaluationformmodel",
            name="hr_marks",
            field=models.FloatField(editable=False, null=True),
        ),
    ]
