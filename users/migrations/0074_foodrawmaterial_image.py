# Generated by Django 5.1.1 on 2025-02-11 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0073_foodrawmaterial_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='foodrawmaterial',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='food_images/'),
        ),
    ]
