# Generated by Django 2.0 on 2017-12-28 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plots', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ASHRAE_targets',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('main_use', models.CharField(max_length=20)),
                ('target', models.IntegerField()),
            ],
        ),
    ]
