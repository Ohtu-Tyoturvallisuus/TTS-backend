# Generated by Django 5.1.1 on 2024-09-19 12:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_rename_risksurvey_survey_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='risknote',
            old_name='Survey',
            new_name='survey',
        ),
        migrations.AddField(
            model_name='risknote',
            name='is_not_relevant',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='risknote',
            name='is_ok',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='survey',
            name='overseer',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='survey',
            name='worksite',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='api.worksite'),
            preserve_default=False,
        ),
    ]