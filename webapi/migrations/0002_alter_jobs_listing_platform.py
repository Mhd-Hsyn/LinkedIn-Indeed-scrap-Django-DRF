# Generated by Django 5.0.2 on 2024-05-18 08:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("webapi", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="jobs",
            name="listing_platform",
            field=models.CharField(
                blank=True,
                choices=[("Indeed", "Indeed"), ("LinkedIn", "LinkedIn")],
                max_length=250,
                null=True,
            ),
        ),
    ]
