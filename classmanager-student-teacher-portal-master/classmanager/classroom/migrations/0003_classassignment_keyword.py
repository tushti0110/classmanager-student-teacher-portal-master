# Generated by Django 4.0.2 on 2022-02-27 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0002_alter_user_first_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='classassignment',
            name='keyword',
            field=models.CharField(default=2, max_length=250),
            preserve_default=False,
        ),
    ]
