# Generated by Django 5.1.3 on 2025-06-29 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_doctorprofile_specialization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctorprofile',
            name='specialization',
            field=models.CharField(choices=[('cardiology', 'cardiology'), ('dermatology', 'dermatology'), ('neurology', 'neurology'), ('pediatrics', 'pediatrics'), ('orthopedics', 'orthopedics'), ('gynecology', 'gynecology'), ('general', 'general Physician'), ('ENT Specialist', 'ENT Specialist')], max_length=100),
        ),
    ]
