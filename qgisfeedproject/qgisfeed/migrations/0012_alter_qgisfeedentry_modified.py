# Generated by Django 4.2.7 on 2023-11-13 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qgisfeed', '0011_alter_qgisfeedentry_created_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qgisfeedentry',
            name='modified',
            field=models.DateTimeField(auto_now=True, db_index=True, verbose_name='Modification date'),
        ),
    ]