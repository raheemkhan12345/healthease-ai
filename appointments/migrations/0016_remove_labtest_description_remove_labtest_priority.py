# Generated by Django 5.1.3 on 2025-07-17 19:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0015_alter_labtest_options_labtest_completed_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='labtest',
            name='description',
        ),
        migrations.RemoveField(
            model_name='labtest',
            name='priority',
        ),
    ]
