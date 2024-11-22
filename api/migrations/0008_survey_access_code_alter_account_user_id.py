# Generated by Django 5.1.2 on 2024-11-22 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_remove_project_project_group_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='access_code',
            field=models.CharField(blank=True, max_length=6, unique=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='user_id',
            field=models.CharField(default='28d4bdf3a55540d4a40896493a20aa87', max_length=64, unique=True),
        ),
    ]
