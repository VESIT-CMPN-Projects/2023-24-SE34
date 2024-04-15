from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from Courses.models import courses
from accounts import constants, decorators
from classes.models import class_course, class_details, class_student
from course_deliverables.models import coursedeliverables
from courseanddeliverables.models import courseanddeliverable
from student_attendance.forms import manageStudentAttendanceTeacherForm
from load_management.models import load_details
from student_attendance.models import student_attendance, student_attendance_details
from academic_sessions.models import session_class
from django.contrib import messages
from classes.models import class_student
from academic_sessions.models import academic_sessions
from django.db.models import Q
from calendar import monthrange
from datetime import datetime, timedelta
import pandas as pd
from django.http import JsonResponse




@login_required(login_url="login")
@decorators.check_user_able_to_see_page(constants.Group.teacher)
def manage_class_attendance_ins_fn(request):
    if request.method == "POST":
        manage_student_attendance_teacher_form = manageStudentAttendanceTeacherForm(request, request.POST)
        att_date_time = request.POST.get('date_time_value')
        print(att_date_time)
        att_date_time_obj = datetime.strptime(att_date_time, '%d-%m-%Y %I:%M %p')
        # print(manage_courses_form["class_program_revision"])
        if manage_student_attendance_teacher_form.is_valid():
            manage_student_attendance_teacher_form_save = manage_student_attendance_teacher_form.save(commit=False)
            manage_student_attendance_teacher_form_save.teacher = request.user
            manage_student_attendance_teacher_form_save.attendance_date_time = att_date_time_obj
            manage_student_attendance_teacher_form_save.created_by = request.user
            manage_student_attendance_teacher_form_save.updated_by = request.user
            manage_student_attendance_teacher_form_save.save()
            student_attendance_save_id = manage_student_attendance_teacher_form_save.id
            messages.success(request,'Attendance Added successfully!')
            return redirect("manage_class_attendance_details_ins_upd", student_attendance_id = student_attendance_save_id)
        else:
            for field_name, errors in manage_student_attendance_teacher_form.errors.items():
                for error_message in errors:
                    print(error_message)
                    messages.error(request, f"{error_message}")
            return redirect("manage_class_attendance_ins")
    manage_student_attendance_teacher_form = manageStudentAttendanceTeacherForm(request)
    manage_student_attendance_teacher_data = student_attendance.objects.filter(created_by = request.user).order_by("-created_dt")
    data = {
        "manage_student_attendance_teacher_form": manage_student_attendance_teacher_form,
        "manage_student_attendance_teacher_data": manage_student_attendance_teacher_data,
    }
    return render(request, "student_attendance/manage_student_attendance.html", data)


@login_required(login_url="login")
@decorators.check_user_able_to_see_page(constants.Group.teacher)
def manage_class_attendance_upd_fn(request, student_attendance_id):
    student_attendance_inst = student_attendance.objects.get(id=student_attendance_id)
    if request.method == "POST":
        manage_student_attendance_teacher_form = manageStudentAttendanceTeacherForm(request, request.POST, instance=student_attendance_inst)
        att_date_time = request.POST.get('date_time_value')
        print(att_date_time)
        att_date_time_obj = ""
        if att_date_time != "":
            att_date_time_obj = datetime.strptime(att_date_time, '%d-%m-%Y %I:%M %p')
        if manage_student_attendance_teacher_form.is_valid():
            manage_student_attendance_teacher_form_save = manage_student_attendance_teacher_form.save(commit=False)
            manage_student_attendance_teacher_form_save.teacher = request.user
            if att_date_time == "":
                manage_student_attendance_teacher_form_save.attendance_date_time = student_attendance_inst.attendance_date_time
            else:
                manage_student_attendance_teacher_form_save.attendance_date_time = att_date_time_obj
            manage_student_attendance_teacher_form_save.created_by = request.user
            manage_student_attendance_teacher_form_save.updated_by = request.user
            manage_student_attendance_teacher_form_save.save()
            messages.success(request,'Attendance updated successfully!')
            return redirect("manage_class_attendance_ins")
        else:
            for field_name, errors in manage_student_attendance_teacher_form.errors.items():
                for error_message in errors:
                    print(error_message)
                    messages.error(request, f"{error_message}")
            return redirect("manage_load_ins")
    manage_student_attendance_teacher_form = manageStudentAttendanceTeacherForm(request, instance=student_attendance_inst)
    manage_student_attendance_teacher_data = student_attendance.objects.filter(created_by = request.user).order_by("-created_dt")
    print(student_attendance_inst.attendance_date_time)
    data = {
        "attendance_date_time": student_attendance_inst.attendance_date_time,
        "manage_student_attendance_teacher_form": manage_student_attendance_teacher_form,
        "manage_student_attendance_teacher_data": manage_student_attendance_teacher_data,
    }
    return render(request, "student_attendance/manage_student_attendance.html", data)
 

@login_required(login_url="login")
@decorators.check_user_able_to_see_page(constants.Group.teacher)
def manage_class_attendance_del_fn(request, student_attendance_id):
    student_attendance_inst = student_attendance.objects.get(id=student_attendance_id)
    student_attendance_inst.delete()
    return redirect("manage_class_attendance_ins")


@login_required(login_url="login")
@decorators.check_user_able_to_see_page(constants.Group.teacher)
def manage_class_attendance_details_ins_upd_fn(request, student_attendance_id):
    student_attendance_inst = student_attendance.objects.get(id=student_attendance_id)
    student_class_inst = class_details.objects.get(class_name = student_attendance_inst.student_class)
    student_class_id = student_class_inst.id
    student_attendance_session_name = student_attendance_inst.academic_session.session_name
    student_attendance_course_name = student_attendance_inst.course.course_name
    student_attendance_cd_name = student_attendance_inst.course_del.cd_name
    student_attendance_class_name = student_attendance_inst.student_class.class_name
    student_attendance_date_time = student_attendance_inst.attendance_date_time
    student_attendance_contents = student_attendance_inst.contents_covered
    student_ids = class_student.objects.filter(stud_class = student_class_id).values_list('student', flat=True)
    students = User.objects.filter(id__in = student_ids)
    student_attendance_details_data = student_attendance_details.objects.filter(student_attendance = student_attendance_id)
    if request.method == "POST":
        student_attendance_checkbox = request.POST.getlist("student_attendance_checkbox")
        print(student_attendance_checkbox)
        student_attendance_details.objects.filter(student_attendance = student_attendance_inst).delete()
        for stud in students:
            print(stud.username)
            if stud.username in student_attendance_checkbox:
                print(stud.first_name,"Present")
                stud_attendance_detail = student_attendance_details.objects.create(
                    student_attendance = student_attendance_inst,
                    student = stud,
                    status = "P",
                    created_by = request.user,
                    updated_by = request.user,
                )
                stud_attendance_detail.save()
            else:
                print(stud.first_name,"Absent")
                stud_attendance_detail = student_attendance_details.objects.create(
                    student_attendance = student_attendance_inst,
                    student = stud,
                    status = "A",
                    created_by = request.user,
                    updated_by = request.user,
                )
                stud_attendance_detail.save()
        messages.success(request,'Student Attendance Details Updated successfully!')
        return redirect("manage_class_attendance_ins")
    print(student_attendance_details_data)
    print(students)
    data = {
        "student_attendance_session_name": student_attendance_session_name,
        "student_attendance_course_name": student_attendance_course_name,
        "student_attendance_cd_name": student_attendance_cd_name,
        "student_attendance_class_name": student_attendance_class_name,
        "student_attendance_date_time": student_attendance_date_time,
        "student_attendance_contents": student_attendance_contents,
        "students": students,
        "student_attendance_details_data": student_attendance_details_data,
    }
    return render(request, "student_attendance/manage_student_attendance_details.html", data)


@login_required(login_url="login")
@decorators.check_user_able_to_see_page(constants.Group.student)
def student_attendance_view_fn(request):
    logged_student = request.user
    print(logged_student)
    class_student_set = class_student.objects.filter(student = logged_student).values_list('stud_class', flat=True)
    print(class_student_set)
    session_class_set = session_class.objects.filter(class_det__in = class_student_set).values_list('session', flat=True)
    print(list(set(session_class_set)))
    sessions = academic_sessions.objects.filter(id__in = list(set(session_class_set)))

    student_attendance_detailed_data = ""
    session_form = ""
    class_course_form = ""
    course_coursedel_form = ""
    student_class_form = ""
    session_form_inst = ""
    class_course_form_inst = ""
    course_coursedel_form_inst = ""
    student_class_form_inst = ""
    if request.method == "POST":
        session_form = request.POST.get("session")
        session_form_inst = academic_sessions.objects.get(id=session_form)
        student_class_form = request.POST.get("student_class")
        student_class_form_inst = class_details.objects.get(id=student_class_form)
        class_course_form = request.POST.get("class_course")
        class_course_form_inst = courses.objects.get(id=class_course_form)
        course_coursedel_form = request.POST.get("course_coursedel")
        course_coursedel_form_inst = coursedeliverables.objects.get(id=course_coursedel_form)
        attendance_list = ""
        if student_class_form == None:
            attendance_list = student_attendance.objects.filter(Q(academic_session = session_form)).order_by("-created_dt")
        elif class_course_form == None:
            attendance_list = student_attendance.objects.filter(Q(academic_session = session_form) & Q(student_class=student_class_form)).order_by("-created_dt")
        elif course_coursedel_form == None:
            attendance_list = student_attendance.objects.filter(Q(academic_session = session_form) & Q(student_class=student_class_form) & Q(course = class_course_form)).order_by("-created_dt")
        else:
            attendance_list = student_attendance.objects.filter(Q(academic_session = session_form) & Q(student_class=student_class_form) & Q(course = class_course_form) & Q(course_del = course_coursedel_form)).order_by("-created_dt")
        print(attendance_list)
        student_attendance_detailed_data = student_attendance_details.objects.filter(Q(student_attendance__in = attendance_list) & Q(student=logged_student)).order_by("-created_dt")
        print(student_attendance_detailed_data)
    
    data = {
        "sessions": sessions,
        "student_attendance_session_name": session_form_inst,
        "student_attendance_course_name": class_course_form_inst,
        "student_attendance_cd_name": course_coursedel_form_inst,
        "student_attendance_class_name": student_class_form_inst,
        "student_attendance_detailed_data": student_attendance_detailed_data,
    }
    return render(request, "student_attendance/manage_student_attendance_view.html", data)

@login_required(login_url="login")
@decorators.check_user_able_to_see_page(constants.Group.superadmin, constants.Group.teacher)
def attendance_view_single_student_wise_fn(request):
    ongoing_sessions = academic_sessions.objects.filter(ongoing="Yes")
    classes_data = class_details.objects.all()
    students = User.objects.filter(groups__name='student')

    if request.method == 'POST':
        selected_session = request.POST.get('session')
        selected_class = request.POST.get('class')
        selected_student = request.POST.get('student')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        start_date = start_date.replace(day=1)
        end_date = end_date.replace(day=monthrange(end_date.year, end_date.month)[1])

        courses_data = courses.objects.filter(
            class_course__class_name_id=selected_class
        )

        students_data = student_attendance_details.objects.filter(
            student_attendance__academic_session_id=selected_session,
            student_attendance__student_class_id=selected_class
        ).values('student__id', 'student__username').distinct()

        attendance_details = student_attendance_details.objects.filter(
            student_attendance__academic_session_id=selected_session,
            student_attendance__student_class_id=selected_class,
            #student_attendance__student_student_id=selected_student,
            student_attendance__attendance_date_time__range=[start_date, end_date]
        )

        lecture_dates = attendance_details.values_list('student_attendance__attendance_date_time', flat=True).distinct()
        lecture_dates = sorted([date.date() for date in lecture_dates])

        if lecture_dates:
            # Create DataFrame and handle potential duplicate entries
            attendance_df = pd.DataFrame(
                list(attendance_details.values('student_attendance__course__course_name', 'student_attendance__attendance_date_time', 'status'))
            )
            attendance_df['student_attendance__attendance_date_time'] = pd.to_datetime(
                attendance_df['student_attendance__attendance_date_time']
            ).dt.date

            # Handle duplicate entries by aggregating them (e.g., using max or sum)
            attendance_df = attendance_df.groupby(['student_attendance__course__course_name', 'student_attendance__attendance_date_time'])['status'].max().reset_index()

            # Pivot the DataFrame
            attendance_pivot = attendance_df.pivot(
                index='student_attendance__course__course_name',
                columns='student_attendance__attendance_date_time',
                values='status'
            )

            attendance_pivot = attendance_pivot.reindex(columns=lecture_dates)
            attendance_pivot.fillna('-', inplace=True)

            # Convert the pivoted DataFrame to a list of dictionaries
            attendance_records = attendance_pivot.reset_index().to_dict(orient='records')
        else:
            attendance_records = []

        data = {
            'sessions': ongoing_sessions,
            'classes': classes_data,
            'students': students_data,
            'selected_session': selected_session,
            'selected_class': selected_class,
            'selected_student': selected_student,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'attendance_records': attendance_records,
            'courses': courses_data,
        }
    else:
        data = {
            'sessions': ongoing_sessions,
            'classes': classes_data,
            'students':students,
            'selected_session': None,
            'selected_class': None,
            'selected_student': None,
            'start_date': None,
            'end_date': None,
            'attendance_records': None,
            'courses': None,
        }

    return render(request, "student_attendance/manage_single_student_attendance_view_for_heads.html", data)


def ajax_fetch_attendance_details(request):
    if request.method == 'POST' and request.is_ajax():
        course = courses.objects.all()
        selected_session = request.POST.get('session')
        selected_class = request.POST.get('student_class')
        selected_student = request.POST.get('student')

        # Fetch attendance details from the database based on selected session, class, and student
        # Filter the attendance data based on the selected session, class, and student name
        attendance_data = student_attendance_details.objects.filter(
            academic_session=selected_session,
            student_class=selected_class,
            student_name=selected_student
        )

        # Serialize the attendance data into JSON format
        attendance_json = [{
            'subject': entry.subject,
            'status': entry.status,
        } for entry in attendance_data]

        return JsonResponse({'attendance': attendance_json})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)



@login_required(login_url="login")
@decorators.check_user_able_to_see_page(constants.Group.superadmin, constants.Group.teacher)
def attendance_view_course_wise_fn(request):
    logged_in_teacher = request.user
    ongoing_sessions = academic_sessions.objects.filter(ongoing="Yes")
    courses_data = courses.objects.filter(load_details__teacher=logged_in_teacher)
    classes_data = class_details.objects.filter(load_details__teacher=logged_in_teacher)

    if request.method == 'POST':
        selected_course = request.POST.get('course')
        selected_session = request.POST.get('session')
        selected_class = request.POST.get('class')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        

        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        start_date = start_date.replace(day=1)
        end_date = end_date.replace(day=monthrange(end_date.year, end_date.month)[1])

        

        # Filter student attendance details based on the selected session, course, class, and date range
        attendance_details = student_attendance_details.objects.filter(
            student_attendance__academic_session_id=selected_session,
            student_attendance__course_id=selected_course,
            student_attendance__student_class_id=selected_class,
            student_attendance__attendance_date_time__range=[start_date, end_date]
        )

        lecture_dates = attendance_details.values_list('student_attendance__attendance_date_time', flat=True).distinct()
        lecture_dates = sorted([date.date() for date in lecture_dates])
        
        if lecture_dates:

            attendance_df = pd.DataFrame(list(attendance_details.values('student__username', 'student_attendance__attendance_date_time', 'status')))
            attendance_df['student_attendance__attendance_date_time'] = pd.to_datetime(attendance_df['student_attendance__attendance_date_time']).dt.date

            # Using Pivot Method in the DataFrame to get student names as rows and lecture dates as columns
            attendance_pivot = attendance_df.pivot(index='student__username', columns='student_attendance__attendance_date_time', values='status')

            attendance_pivot = attendance_pivot.reindex(columns=lecture_dates)

            attendance_pivot.fillna('-', inplace=True)

            attendance_records = attendance_pivot.reset_index().to_dict(orient='records')

        else:
            attendance_records = []

        print(attendance_records)

        data = {
            'sessions': ongoing_sessions,
            'courses': courses_data,
            'classes': classes_data,
            'selected_session': selected_session,
            'selected_course': selected_course,
            'selected_class': selected_class,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'attendance_records': attendance_records,
        }
    else:
        data = {
            'sessions': ongoing_sessions,
            'courses': courses_data,
            'classes': classes_data,
            'selected_session': None,
            'selected_course': None,
            'selected_class': None,
            'start_date': None,
            'end_date': None,
            'attendance_records': None,
        }

    return render(request, "student_attendance/manage_course_wise_student_attendance_view_for_heads.html", data)


def ajax_load_class_from_session(request):
    academic_session_id = request.GET.get("academic_session_id")
    #print(academic_session_id)
    class_data = class_details.objects.filter(
                    id__in=load_details.objects.filter(session = academic_session_id).values_list('student_class', flat=True)
                ).order_by(
                    "-created_dt"
                )
    #print(class_data)
    return render(
        request,
        "generic/class_dropdown_list_options.html",
        {"classes": class_data},
    )

def ajax_load_course_del_from_course(request):
    course_id = request.GET.get("course_id")
    #print(course_id)
    deliverable_data = coursedeliverables.objects.filter(
                    id__in=courseanddeliverable.objects.filter(course = course_id).values_list('deliverable', flat=True)
                ).order_by(
                    "-created_dt"
                )
    #print(deliverable_data)
    return render(
        request,
        "generic/course_del_dropdown_list_options.html",
        {"course_deliverables": deliverable_data},
    )

def ajax_load_course_from_class(request):
    class_id = request.GET.get("class_id")
    #print(class_id)
    course_data = courses.objects.filter(
        id__in=class_course.objects.filter(
            class_name = class_id).values_list('course', flat=True)).order_by("-created_dt")
    #print(course_data)
    return render(
        request,
        "generic/course_dropdown_list_options.html",
        {"courses": course_data},
    )

def ajax_load_class_from_session_student_view(request):
    logged_student = request.user
    print(logged_student)
    class_student_set = class_student.objects.filter(student = logged_student).values_list('stud_class', flat=True)
    print(class_student_set)
    academic_session_id = request.GET.get("academic_session_id")
    print(academic_session_id)
    class_data = class_details.objects.filter(Q(
                    id__in = class_student.objects.filter(student = logged_student).values_list('stud_class', flat=True)) & Q(id__in = session_class.objects.filter(session = academic_session_id).values_list('class_det', flat=True))).order_by(
                    "-created_dt"
                )
    print(class_data)
    return render(
        request,
        "generic/class_dropdown_list_options.html",
        {"classes": class_data},
    )

def ajax_load_course_from_class_student_view(request):
    class_id = request.GET.get("class_id")
    print(class_id)
    course_data = courses.objects.filter(
        id__in=class_course.objects.filter(
            class_name = class_id).values_list('course', flat=True)).order_by("-created_dt")
    print(course_data)
    return render(
        request,
        "generic/course_dropdown_list_options.html",
        {"courses": course_data},
    )

def ajax_load_del_from_course_student_view(request):
    course_id = request.GET.get("course_id")
    print(course_id)
    course_del_data = coursedeliverables.objects.filter(
                    id__in=courseanddeliverable.objects.filter(course = course_id).values_list('deliverable', flat=True)
                ).order_by(
                    "-created_dt"
                )
    print(course_del_data)
    return render(
        request,
        "generic/course_del_dropdown_list_options.html",
        {"course_deliverables": course_del_data},
    )

