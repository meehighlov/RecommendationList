# Generated by Django 2.2.3 on 2019-07-24 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_remove_customuser_refresh_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='refresh_token',
            field=models.CharField(default='', max_length=500),
        ),
    ]