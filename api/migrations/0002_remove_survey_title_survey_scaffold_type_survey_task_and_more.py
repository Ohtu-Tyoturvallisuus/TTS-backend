# Generated by Django 5.1.1 on 2024-10-03 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='survey',
            name='title',
        ),
        migrations.AddField(
            model_name='survey',
            name='scaffold_type',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='survey',
            name='task',
            field=models.TextField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='survey',
            name='description',
            field=models.TextField(max_length=250),
        ),
    ]
