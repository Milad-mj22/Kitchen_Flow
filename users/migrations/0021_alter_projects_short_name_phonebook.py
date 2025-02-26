# Generated by Django 4.1.2 on 2023-07-07 17:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0019_projects_city_alter_projects_project_maanger"),
    ]

    operations = [
        migrations.AlterField(
            model_name="projects",
            name="short_name",
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.CreateModel(
            name="PhoneBook",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=200)),
                ("last_name", models.CharField(max_length=200)),
                ("phone_number", models.IntegerField()),
                ("description", models.CharField(max_length=3000, null=True)),
                ("position", models.CharField(max_length=3000)),
                (
                    "project",
                    models.ForeignKey(
                        blank=True,
                        default=1,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="project",
                        to="users.projects",
                    ),
                ),
            ],
            options={
                "ordering": ["-first_name"],
            },
        ),
    ]
