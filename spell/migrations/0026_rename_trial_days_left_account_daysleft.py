# Generated by Django 4.0.3 on 2022-07-28 15:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spell', '0025_account_trial_days_left'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='trial_days_left',
            new_name='daysleft',
        ),
    ]
