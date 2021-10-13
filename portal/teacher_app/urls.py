from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('teachers', views.TeachersView.as_view(), name='teachers_list'),
    path('teacher/upload/', views.UploadTeachersView.as_view(), name="teacher_upload"),
    path('teacher/view/<int:pk>/', views.TeacherProfileView.as_view(), name='teacher_view'),
    path('<tagname>', views.ErrorView.as_view(), name='other_view')
]
