# Generated by Django 2.2.8 on 2020-05-21 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('question', '0003_report_poll'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='report_id',
            field=models.BigIntegerField(blank=True, null=True, unique=True),
        ),
    ]
