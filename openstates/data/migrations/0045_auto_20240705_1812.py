# Generated by Django 3.2.14 on 2024-07-05 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0044_bill_citations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventdocument',
            name='note',
            field=models.TextField(),
        ),
        migrations.AddIndex(
            model_name='voteevent',
            index=models.Index(fields=['dedupe_key'], name='opencivicdata_voteevent_dedupe__75a90b_idx'),
        ),
    ]
