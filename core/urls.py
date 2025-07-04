# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from . import views

urlpatterns = [
    path('', welcome, name='welcome'),    # Root shows welcome page
    path('home/', home, name='home'),   # change your home view to /home/
     path('student/setup/', student_profile_setup, name='student_setup'),
     path('select-company/', views.select_company_view, name='select_company'),
]
