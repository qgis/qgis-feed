# Generated by Django 4.2.6 on 2023-11-03 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qgisfeed', '0009_characterlimitconfiguration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qgisfeedentry',
            name='url',
            field=models.URLField(blank=True, help_text='URL for more information link', null=True, verbose_name='URL'),
        ),
    ]
