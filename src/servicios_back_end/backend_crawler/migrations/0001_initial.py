# Generated by Django 3.0.2 on 2020-05-31 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Trabajos_terminados',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bitacora', models.CharField(max_length=50)),
                ('idEminus', models.CharField(max_length=100)),
                ('usuario', models.CharField(max_length=20)),
                ('periodo', models.CharField(max_length=100)),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
    ]
