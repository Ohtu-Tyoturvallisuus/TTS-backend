# Generated by Django 5.1.1 on 2024-09-25 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_alter_survey_overseer'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='scaffold_risks',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='survey',
            name='surroundinds_risks',
            field=models.JSONField(default=dict),
        ),
    ]