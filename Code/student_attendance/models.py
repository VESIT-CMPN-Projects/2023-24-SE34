from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from Courses.models import courses
from academic_sessions.models import academic_sessions
from course_deliverables.models import coursedeliverables
from classes.models import class_details

# Create your models here.


class student_attendance(models.Model):
    academic_session = models.ForeignKey(
        academic_sessions, on_delete=models.SET_NULL, null=True, related_name="stud_attendance_academic_session")
    student_class = models.ForeignKey(
        class_details, on_delete=models.SET_NULL, null=True, related_name="stud_attendance_class")
    teacher = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="stud_attendance_teacher")
    course = models.ForeignKey(
        courses, on_delete=models.SET_NULL, null=True)
    course_del = models.ForeignKey(
        coursedeliverables, on_delete=models.SET_NULL, null=True)
    attendance_date_time = models.DateTimeField(null=True, blank=True)
    contents_covered = models.CharField(max_length=100)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="stud_attendance_created_by",
    )
    created_dt = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="stud_attendance_updated_by"
    )
    updated_dt = models.DateTimeField(auto_now=True)


class student_attendance_details(models.Model):
    student_attendance = models.ForeignKey(
        student_attendance, on_delete=models.CASCADE, null=True, related_name="stud_attendance_details")
    student = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="stud_attendance_details")
    status = models.CharField(max_length=10)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="stud_attendance_details_created_by",
    )
    created_dt = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="stud_attendance_details_updated_by"
    )
    updated_dt = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student_attendance', 'student'], name='unique_student_attendace_and_student'),
        ]