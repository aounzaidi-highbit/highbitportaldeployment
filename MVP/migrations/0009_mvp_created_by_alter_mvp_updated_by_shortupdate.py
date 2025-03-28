# Generated by Django 4.0.6 on 2024-07-22 13:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0028_alter_employee_confirmation_date'),
        ('MVP', '0008_activity_changes_activity_remarks_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='mvp',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_mvps', to='website.employee'),
        ),
        migrations.AlterField(
            model_name='mvp',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='updated_mvps', to='website.employee'),
        ),
        migrations.CreateModel(
            name='ShortUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('Success', 'Success'), ('Fail', 'Fail'), ('Pending', 'Pending')], max_length=100)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='website.employee')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.teams')),
            ],
            options={
                'verbose_name': 'Short Update',
                'verbose_name_plural': 'Short Updates',
            },
        ),
    ]
