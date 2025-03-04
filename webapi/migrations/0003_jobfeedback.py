# Generated by Django 5.0.2 on 2024-05-18 10:35

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("webapi", "0002_alter_jobs_listing_platform"),
    ]

    operations = [
        migrations.CreateModel(
            name="JobFeedback",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("feedback", models.TextField(blank=True, null=True)),
                (
                    "admin_id",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="webapi.superadmin",
                    ),
                ),
                (
                    "job",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="feedbacks",
                        to="webapi.jobs",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
