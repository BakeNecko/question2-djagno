# Generated by Django 2.2.8 on 2020-05-21 11:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('question', '0002_auto_20200521_1101'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='poll',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='question.Poll'),
            preserve_default=False,
        ),
    ]
