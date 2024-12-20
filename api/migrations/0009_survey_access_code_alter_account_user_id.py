# Generated by Django 5.1.2 on 2024-11-27 10:14

import api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_account_user_id_alter_survey_scaffold_type_and_more'),
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
            field=models.CharField(default=api.models.generate_uuid, max_length=64, unique=True),
        ),
    ]
