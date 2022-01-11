# Generated by Django 3.2 on 2021-05-27 21:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("data", "0035_auto_20210422_1926"),
        ("people_admin", "0006_alter_persondelta_data_changes"),
    ]

    operations = [
        migrations.CreateModel(
            name="PersonRetirement",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.CharField(max_length=10)),
                ("is_dead", models.BooleanField()),
                ("is_vacant", models.BooleanField()),
                ("reason", models.TextField()),
                (
                    "delta_set",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="person_retirements",
                        to="people_admin.deltaset",
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="data.person"
                    ),
                ),
            ],
        ),
    ]
