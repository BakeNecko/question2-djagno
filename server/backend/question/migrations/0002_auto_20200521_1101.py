# Generated by Django 2.2.8 on 2020-05-21 11:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('question', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='report',
            old_name='MyUser_report_id',
            new_name='user_report_id',
        ),
    ]
