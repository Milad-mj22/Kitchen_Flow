# Generated by Django 5.0.7 on 2024-10-10 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0061_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='allowedlocation',
            name='locations',
        ),
        migrations.AddField(
            model_name='allowedlocation',
            name='locations',
            field=models.ManyToManyField(related_name='allowed_locations', to='users.location'),
        ),
    ]
