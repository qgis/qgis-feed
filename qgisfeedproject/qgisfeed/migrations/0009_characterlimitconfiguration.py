# Generated by Django 4.2.6 on 2023-10-27 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qgisfeed', '0008_dailyqgisuservisit'),
    ]

    operations = [
        migrations.CreateModel(
            name='CharacterLimitConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_name', models.CharField(max_length=255, unique=True)),
                ('max_characters', models.PositiveIntegerField()),
            ],
        ),
    ]
