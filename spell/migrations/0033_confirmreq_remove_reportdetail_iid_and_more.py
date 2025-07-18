# Generated by Django 4.0.3 on 2022-08-13 01:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('spell', '0032_account_children_account_parent'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfirmReq',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fname', models.TextField(max_length=300)),
                ('lname', models.TextField(max_length=300)),
                ('username', models.TextField(max_length=300)),
                ('email', models.TextField(max_length=300)),
                ('parent', models.IntegerField(blank=True, null=True)),
                ('lock1', models.IntegerField()),
                ('lock2', models.IntegerField()),
            ],
        ),
        migrations.RemoveField(
            model_name='reportdetail',
            name='iid',
        ),
        migrations.AddField(
            model_name='reportdetail',
            name='report',
            field=models.ForeignKey(default=435, on_delete=django.db.models.deletion.CASCADE, to='spell.report'),
            preserve_default=False,
        ),
    ]
