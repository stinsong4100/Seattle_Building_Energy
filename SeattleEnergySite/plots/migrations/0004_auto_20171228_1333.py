# Generated by Django 2.0 on 2017-12-28 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plots', '0003_auto_20171228_1053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='building',
            name='Tax_PIN',
            field=models.IntegerField(),
        ),
    ]