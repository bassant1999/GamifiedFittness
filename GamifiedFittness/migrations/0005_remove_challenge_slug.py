# Generated by Django 5.1.4 on 2025-01-17 20:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('GamifiedFittness', '0004_remove_goal_end_date_remove_goal_start_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='challenge',
            name='slug',
        ),
    ]
