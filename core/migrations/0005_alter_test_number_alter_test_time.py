# Generated by Django 5.2 on 2025-04-18 21:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_test_mode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='number',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='test',
            name='time',
            field=models.IntegerField(),
        ),
    ]
