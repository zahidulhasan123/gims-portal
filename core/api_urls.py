from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, CompanyViewSet, AcademicSupervisorViewSet, IndustrialSupervisorViewSet, MarksViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'academic-supervisors', AcademicSupervisorViewSet)
router.register(r'industrial-supervisors', IndustrialSupervisorViewSet)
router.register(r'marks', MarksViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
