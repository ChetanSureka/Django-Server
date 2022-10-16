# Generated by Django 4.1.1 on 2022-10-12 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("firstname", models.CharField(max_length=100)),
                ("lastname", models.CharField(max_length=100)),
                ("is_active", models.BooleanField(default=True)),
                ("is_admin", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "User",
                "verbose_name_plural": "Users",
            },
        ),
    ]
