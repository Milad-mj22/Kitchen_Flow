# Generated by Django 4.2.13 on 2024-07-25 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0035_snappfoodlist'),
    ]

    operations = [
        migrations.CreateModel(
            name='FoodRawMaterial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('data', models.JSONField()),
            ],
            options={
                'ordering': ['-name'],
            },
        ),
    ]
