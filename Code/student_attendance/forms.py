from django import forms
from Courses.models import courses
from course_deliverables.models import coursedeliverables
from courseanddeliverables.models import courseanddeliverable
from users.models import teacher_profile
from institutes.models import Institute_Details
from classes.models import class_details
from .models import student_attendance
from django.contrib.auth.models import User
from academic_sessions.models import academic_sessions
from load_management.models import load_details
from Courses.models import courses
from django.db.models import Q

class manageStudentAttendanceTeacherForm(forms.ModelForm):
    class Meta:
        model = student_attendance
        fields = ["academic_session", "student_class", "course", "course_del", "contents_covered"]
        labels = {
            "academic_session": "Academic Session",
            "student_class": "Class",
            "course": "Course",
            "course_del": "Course Deliverable",
            "contents_covered": "Contents Covered"
        }
        help_text = {
            "academic_session": "Select the Academic Session",
            "student_class": "Select the Class",
            "course": "Select the Course",
            "course_del": "Select the Course Deliverable",
            "contents_covered": "Enter the Contents Covered"
        }
        error_messages = {
            "academic_session": {"required": "Select the Academic Session"},
            "student_class": {"required": "Select the Class"},
            "course": {"required": "Select the Course"},
            "course_del": {"required": "Select the Course Deliverable"},
            "contents_covered": {"required": "Enter the Contents Covered"},

        }
        status_choices = (
            ("", "None"),
            ("1", "Present"),
            ("0", "Absent"),
        )

        widgets = {
            "academic_session": forms.Select(
                attrs={
                    "class": "form-control",
                    "style": "width: 100%; margin-bottom: 20px;",
                    "placeholder": "Select the Academic Session",
                }
            ),
            "student_class": forms.Select(
                attrs={
                    "class": "form-control",
                    "style": "width: 100%; margin-bottom: 20px;",
                    "placeholder": "Select the Class",
                }
            ),
            "course": forms.Select(
                attrs={
                    "class": "form-control",
                    "style": "width: 100%; margin-bottom: 20px;",
                    "placeholder": "Select the Course",
                }
            ),
            "course_del": forms.Select(
                attrs={
                    "class": "form-control",
                    "style": "width: 100%; margin-bottom: 20px;",
                    "placeholder": "Select the Course Deliverable",
                }
            ),
            "contents_covered": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "width: 100%; margin-bottom: 20px;",
                    "placeholder": "Contents Covered",
                }
            ),
        }

    def __init__(self, request, *args, **kwargs):
        super(manageStudentAttendanceTeacherForm, self).__init__(*args, **kwargs)
        print(request)
        teacher = teacher_profile.objects.get(teacher = request.user)
        inst_details = Institute_Details.objects.get(id = teacher.institute.id)
        academic_session = academic_sessions.objects.filter(
            Q(created_by=inst_details.created_by) & Q(ongoing="Yes")
        )
        self.fields["academic_session"].queryset = academic_session
        
        if "academic_session" in self.data:
            try:
                academic_session_id = int(self.data.get("academic_session"))
                print(academic_session_id)
                self.fields[
                    "student_class"
                ].queryset = class_details.objects.filter(
                    id__in=load_details.objects.filter(session = academic_session_id).values_list('class_name', flat=True)
                ).order_by(
                    "-created_dt"
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            #print("Hello")
            self.fields[
                "student_class"
            ].queryset = class_details.objects.filter(created_by=inst_details.created_by)

        if "student_class" in self.data:
            try:
                student_class_id = int(self.data.get("student_class"))
                #print(student_class_id)
                self.fields[
                    "course"
                ].queryset = courses.objects.filter(
                    id__in=load_details.objects.filter(class_name = student_class_id).values_list('course', flat=True)
                ).order_by(
                    "-created_dt"
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            #print("Hello")
            self.fields[
                "course"
            ].queryset = courses.objects.filter(created_by=inst_details.created_by)

        if "course" in self.data:
            try:
                course_id = int(self.data.get("course"))
                #print(course_id)
                self.fields[
                    "course_del"
                ].queryset = coursedeliverables.objects.filter(
                    id__in=courseanddeliverable.objects.filter(course = course_id).values_list('deliverable', flat=True)
                ).order_by(
                    "-created_dt"
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            #print("Hello")
            self.fields[
                "course_del"
            ].queryset = coursedeliverables.objects.filter(created_by=inst_details.created_by)
