# core/middleware.py

from django.utils.deprecation import MiddlewareMixin
from .models import Semester, Student

class UpdateStudentSemesterMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            try:
                student = request.user.student
                active_semester = Semester.objects.filter(is_active=True).first()
                if active_semester and student.semester != active_semester:
                    student.semester = active_semester
                    student.save(update_fields=['semester'])
            except Student.DoesNotExist:
                pass  # user has no student profile, ignore
