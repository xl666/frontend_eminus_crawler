# Generated by Django 3.0.2 on 2020-04-28 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bd', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ips',
            name='intentos',
            field=models.IntegerField(default=0),
        ),
    ]