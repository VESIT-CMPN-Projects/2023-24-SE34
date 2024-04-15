from django.contrib import admin
from django.urls import path
from student_attendance import views as student_attendance_views

urlpatterns = [
    path(
        "manage-class-attendance-ins",
        student_attendance_views.manage_class_attendance_ins_fn,
        name="manage_class_attendance_ins",
    ),
    path(
        "manage-class-attendance-upd/<int:student_attendance_id>",
        student_attendance_views.manage_class_attendance_upd_fn,
        name="manage_class_attendance_upd",
    ),

    path(
        "manage-class-attendance-del/<int:student_attendance_id>",
        student_attendance_views.manage_class_attendance_del_fn,
        name="manage_class_attendance_del",
    ),

    path(
        "manage-class-attendance-details-ins-upd/<int:student_attendance_id>",
        student_attendance_views.manage_class_attendance_details_ins_upd_fn,
        name="manage_class_attendance_details_ins_upd",
    ),
    path(
        "student-attendance-view",
        student_attendance_views.student_attendance_view_fn,
        name="student_attendance_view",
    ),
   path(
        'manage-course-wise-student-attendance-view-for-heads/',
        student_attendance_views.attendance_view_course_wise_fn,
        name='manage_course_wise_student_attendance_view_for_heads'
    ),

    path(
        "manage-single-student-attendance-view-for-heads",
        student_attendance_views.attendance_view_single_student_wise_fn,
        name="manage_single_student_attendance_view_for_heads",
    ),
    
    path(
        "ajax-fetch-attendance-details",
        student_attendance_views.ajax_fetch_attendance_details,
        name="ajax_fetch_attendance_details",
    ),


    path('ajax/load-course-from-class/', student_attendance_views.ajax_load_course_from_class, name='ajax_load_course_from_class'), # AJAX
    path('ajax/load-course-del-from-course/', student_attendance_views.ajax_load_course_del_from_course, name='ajax_load_course_del_from_course'), # AJAX
    path('ajax/load-class-from-session/', student_attendance_views.ajax_load_class_from_session, name='ajax_load_class_from_session'), # AJAX
    path('ajax/load-class-from-session-student-view/', student_attendance_views.ajax_load_class_from_session_student_view, name='ajax_load_class_from_session_student_view'), # AJAX
    path('ajax/load-course-from-class-student-view/', student_attendance_views.ajax_load_course_from_class_student_view, name='ajax_load_course_from_class_student_view'), # AJAX
    path('ajax/load-del-from-course-student-view/', student_attendance_views.ajax_load_del_from_course_student_view, name='ajax_load_del_from_course_student_view'), # AJAX
    
]
