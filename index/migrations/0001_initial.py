# Generated by Django 2.2.2 on 2019-06-27 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='daily_bandwidth',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(max_length=5)),
                ('bandwidth', models.CharField(max_length=30)),
            ],
        ),
    ]