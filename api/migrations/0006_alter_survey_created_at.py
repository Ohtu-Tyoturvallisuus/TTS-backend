# Generated by Django 5.1.1 on 2024-09-23 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_remove_risknote_is_not_relevant_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='survey',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
