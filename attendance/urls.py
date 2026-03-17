from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'lecturers', views.LecturerViewSet, basename='lecturer')
router.register(r'students', views.StudentViewSet, basename='student')
router.register(r'courses', views.CourseViewSet, basename='course')
router.register(r'attendances', views.AttendanceViewSet, basename='attendance')
router.register(r'attendance-tokens', views.AttendanceTokenViewSet, basename='attendance-token')

urlpatterns = [
    path('', include(router.urls)),
    path('studentenrolledcourses/', views.StudentEnrolledCoursesView.as_view(), name='student_enrolled_courses'),
    path('login/student/', views.StudentLoginView.as_view(), name='student_login'),
    path('login/staff/', views.StaffLoginView.as_view(), name='staff_login'),
    path('logout/', views.LogoutView.as_view(), name='api_logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('submit-location/', views.SubmitLocationView.as_view(), name='submit_location'),
    path('student-attendance-history/', views.StudentAttendanceHistoryView.as_view(), name='student_attendance_history'),
    path('lecturer-attendance-history/', views.LecturerAttendanceHistoryView.as_view(), name='lecturer_attendance_history'),
    path('lecturer-location/', views.LecturerLocationView.as_view(), name='lecturer_location'),
]
