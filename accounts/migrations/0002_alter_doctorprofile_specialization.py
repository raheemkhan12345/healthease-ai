# Generated by Django 5.1.3 on 2025-06-29 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctorprofile',
            name='specialization',
            field=models.CharField(choices=[('Cardiology', 'Cardiology'), ('Dermatology', 'Dermatology'), ('Neurology', 'Neurology'), ('Pediatrics', 'Pediatrics'), ('Orthopedics', 'Orthopedics'), ('Gynecology', 'Gynecology'), ('General', 'General Physician')], max_length=100),
        ),
    ]
