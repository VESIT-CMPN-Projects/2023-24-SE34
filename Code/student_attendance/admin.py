from django.contrib import admin

# Register your models here.
from . models import student_attendance,student_attendance_details
# Register your models here.
admin.site.register(student_attendance)
admin.site.register(student_attendance_details)