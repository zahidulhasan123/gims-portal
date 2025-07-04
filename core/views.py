from django.shortcuts import render

# Create your views here.
# core/views.py
from rest_framework import viewsets
from .models import Student, Company, AcademicSupervisor, IndustrialSupervisor, Marks
from .serializers import *


from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import Student, Company, IndustrialSupervisor
from .serializers import StudentSerializer, IndustrialSupervisorSerializer
from django.shortcuts import get_object_or_404

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def get_permissions(self):
        if self.action in ['list', 'by_student_id']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request):
        # Associate current user with student
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def me(self, request):
        student = get_object_or_404(Student, user=request.user)
        serializer = self.get_serializer(student)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def select_company(self, request, pk=None):
        student = self.get_object()
        if student.company:
            return Response({'error': 'Company already selected.'}, status=400)

        company_id = request.data.get('company_id')
        company = get_object_or_404(Company, id=company_id)

        if company.total_seats - company.seats_taken <= 0:
            return Response({'error': 'No available seats.'}, status=400)

        student.company = company
        company.seats_taken += 1
        company.save()
        student.save()

        return Response({'success': 'Company assigned successfully.'})

    @action(detail=True, methods=['post'])
    def add_industrial_supervisor(self, request, pk=None):
        student = self.get_object()
        serializer = IndustrialSupervisorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        supervisor = serializer.save()
        student.industrial_supervisor = supervisor
        student.save()
        return Response({'success': 'Supervisor added.'})

    @action(detail=False, methods=['get'], url_path='by-student-id/(?P<student_id>[^/.]+)')
    def by_student_id(self, request, student_id=None):
        student = get_object_or_404(Student, student_id=student_id)
        serializer = self.get_serializer(student)
        return Response(serializer.data)

class AcademicSupervisorViewSet(viewsets.ModelViewSet):
    queryset = AcademicSupervisor.objects.all()
    serializer_class = AcademicSupervisorSerializer

class IndustrialSupervisorViewSet(viewsets.ModelViewSet):
    queryset = IndustrialSupervisor.objects.all()
    serializer_class = IndustrialSupervisorSerializer

class MarksViewSet(viewsets.ModelViewSet):
    queryset = Marks.objects.all()
    serializer_class = MarksSerializer


from django.shortcuts import render
from django.contrib.auth.decorators import login_required


from django.shortcuts import render, redirect
from .models import Semester, InternshipSelection

from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import Student, Semester, InternshipSelection

@login_required
def home(request):
    # Check if the user has an associated student profile
    if not hasattr(request.user, 'student'):
        return redirect('student_setup')  # redirect to student profile setup page

    student = request.user.student
    active_semester = Semester.objects.filter(is_active=True).first()

    internship_selection = None
    if active_semester:
        internship_selection = InternshipSelection.objects.filter(
            student=student,
            semester=active_semester
        ).select_related('company').first()

    # Enrich student object with dynamic properties
    student.has_selected_company = internship_selection is not None
    student.company = internship_selection.company if internship_selection else None
    student.self_managed_company_name = internship_selection.self_managed_company_name if internship_selection else None

    return render(request, 'core/home.html', {'student': student})



from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def landing(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('social:begin', backend='google-oauth2')
    

def welcome(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'core/welcome.html')





from .forms import StudentProfileForm
from django.contrib.auth.decorators import login_required

@login_required
def student_profile_setup(request):
    if hasattr(request.user, 'student'):
        return redirect('home')

    if request.method == 'POST':
        form = StudentProfileForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.user = request.user
            student.email = request.user.email  # ✅ auto-set from Google account
            student.save()
            return redirect('home')
    else:
        form = StudentProfileForm()

    return render(request, 'core/student_setup.html', {'form': form})

from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import render, redirect
from .models import CompanySemesterInfo, InternshipSelection, Semester

from django.db.models import F, ExpressionWrapper, IntegerField
from django.db.models import F, ExpressionWrapper, IntegerField

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import F, ExpressionWrapper, IntegerField
from .models import Semester, CompanySemesterInfo, InternshipSelection

# @login_required
# def select_company_view(request):
#     student = request.user.student

#     # Get the active semester (there should be exactly one active)
#     active_semester = Semester.objects.filter(is_active=True).first()
#     if not active_semester:
#         return render(request, 'core/select_company.html', {
#             'companies': [],
#             'error': 'No active semester found.'
#         })

#     # Ensure student's semester is set to active semester
#     if student.semester != active_semester:
#         student.semester = active_semester
#         student.save(update_fields=['semester'])

#     # Check if student already selected a company for this semester
#     if InternshipSelection.objects.filter(student=student, semester=active_semester).exists():
#         return redirect('home')  # or show a message

#     if request.method == 'POST':
#         company_id = request.POST.get('company_id')
#         csi = CompanySemesterInfo.objects.filter(
#             company_id=company_id,
#             semester=active_semester,
#             seats_taken__lt=F('total_seats')
#         ).first()

#         if not csi:
#             companies = CompanySemesterInfo.objects.filter(
#                 semester=active_semester,
#                 seats_taken__lt=F('total_seats')
#             ).select_related('company').annotate(
#                 available_seats=ExpressionWrapper(
#                     F('total_seats') - F('seats_taken'),
#                     output_field=IntegerField()
#                 )
#             )
#             return render(request, 'core/select_company.html', {
#                 'companies': companies,
#                 'error': 'Selected company is not available or full.'
#             })

#         # Save the internship selection
#         InternshipSelection.objects.create(
#             student=student,
#             semester=active_semester,
#             company=csi.company,
#         )

#         # Increment seats taken
#         csi.seats_taken = F('seats_taken') + 1
#         csi.save()

#         return redirect('home')

#     # GET request — show all companies with available seats for the active semester
#     companies = CompanySemesterInfo.objects.filter(
#         semester=active_semester,
#         seats_taken__lt=F('total_seats')
#     ).select_related('company').annotate(
#         available_seats=ExpressionWrapper(
#             F('total_seats') - F('seats_taken'),
#             output_field=IntegerField()
#         )
#     )

#     return render(request, 'core/select_company.html', {'companies': companies})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import F, ExpressionWrapper, IntegerField
from .models import CompanySemesterInfo, InternshipSelection, Semester

@login_required
def select_company_view(request):
    student = request.user.student

    # Always fetch the active semester
    current_semester = Semester.objects.filter(is_active=True).first()
    if not current_semester:
        return render(request, 'core/select_company.html', {
            'error': 'No active semester found.',
            'companies': [],
        })

    # Check if student already selected
    if InternshipSelection.objects.filter(student=student, semester=current_semester).exists():
        return redirect('home')

    if request.method == 'POST':
        selection_type = request.POST.get('selection_type')

        if selection_type == 'self':
            name = request.POST.get('self_company_name')
            details = request.POST.get('self_company_details')

            if not name or not details:
                return render(request, 'core/select_company.html', {
                    'error': 'Both name and details are required for self-managed companies.',
                    'companies': [],
                })

            InternshipSelection.objects.create(
                student=student,
                semester=current_semester,
                self_managed_company_name=name,
                self_managed_company_details=details,
            )
            return redirect('home')

        elif selection_type == 'system':
            company_id = request.POST.get('company_id')
            csi = CompanySemesterInfo.objects.filter(
                company_id=company_id,
                semester=current_semester,
                seats_taken__lt=F('total_seats')
            ).select_related('company').first()

            if not csi:
                companies = CompanySemesterInfo.objects.filter(
                    semester=current_semester,
                    seats_taken__lt=F('total_seats')
                ).select_related('company').annotate(
                    available_seats=ExpressionWrapper(F('total_seats') - F('seats_taken'), output_field=IntegerField())
                )

                return render(request, 'core/select_company.html', {
                    'companies': companies,
                    'error': 'Selected company is not available or is full.'
                })

            InternshipSelection.objects.create(
                student=student,
                semester=current_semester,
                company=csi.company,
            )

            # ✅ Properly update seat count using F()
            CompanySemesterInfo.objects.filter(id=csi.id).update(seats_taken=F('seats_taken') + 1)

            return redirect('home')

    # On GET, show available companies
    companies = CompanySemesterInfo.objects.filter(
        semester=current_semester,
        seats_taken__lt=F('total_seats')
    ).select_related('company').annotate(
        available_seats=ExpressionWrapper(F('total_seats') - F('seats_taken'), output_field=IntegerField())
    )

    return render(request, 'core/select_company.html', {
        'companies': companies,
    })
