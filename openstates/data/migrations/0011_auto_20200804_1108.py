from django.db import migrations, models
import django.db.models.deletion
from ...metadata import lookup


def forwards_func(apps, schema_editor):
    # copy cities into jurisdiction ids
    Person = apps.get_model("data", "Person")

    for p in Person.objects.exclude(current_state=""):
        p.current_jurisdiction_id = lookup(abbr=p.current_state).jurisdiction_id
        p.save()


class Migration(migrations.Migration):

    dependencies = [("data", "0010_auto_20200721_1604")]

    operations = [
        migrations.AddField(
            model_name="person",
            name="current_jurisdiction",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="current_people",
                to="data.Jurisdiction",
            ),
        ),
        migrations.RunPython(forwards_func),
    ]
