# Generated by Django 4.0.3 on 2022-08-13 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spell', '0033_confirmreq_remove_reportdetail_iid_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='confirmreq',
            name='password',
            field=models.CharField(default='fun', max_length=255),
            preserve_default=False,
        ),
    ]
