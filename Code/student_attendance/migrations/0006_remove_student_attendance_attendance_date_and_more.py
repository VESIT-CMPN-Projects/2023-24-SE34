# Generated by Django 4.1.5 on 2023-11-22 18:12

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student_attendance', '0005_remove_student_attendance_staff_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student_attendance',
            name='attendance_date',
        ),
        migrations.AddField(
            model_name='student_attendance',
            name='attendance_date_time',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now),
        ),
    ]
