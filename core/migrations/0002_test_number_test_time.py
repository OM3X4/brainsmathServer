# Generated by Django 5.2 on 2025-04-16 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='number',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='test',
            name='time',
            field=models.IntegerField(null=True),
        ),
    ]
