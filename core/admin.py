from django.contrib import admin
from .models import Student, Company, AcademicSupervisor, IndustrialSupervisor, Marks

from django.contrib import admin
from .models import Student, Semester, InternshipSelection

class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'name', 'email', 'phone', 'current_company']
    list_filter = ['semester']  # make sure this is a list or tuple

    def current_company(self, obj):
        active_sem = Semester.objects.filter(is_active=True).first()
        if not active_sem:
            return "No active semester"

        selection = InternshipSelection.objects.filter(student=obj, semester=active_sem).first()
        if not selection:
            return "No company selected"

        if selection.company:
            return selection.company.name
        elif selection.self_managed_company_name:
            return f"Self-managed: {selection.self_managed_company_name}"
        else:
            return "Not assigned"

    current_company.short_description = "Company"

admin.site.register(Student, StudentAdmin)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'total_seats', 'seats_taken')
    search_fields = ('name', 'location')
    list_filter = ('location',)

admin.site.register(AcademicSupervisor)
admin.site.register(IndustrialSupervisor)
admin.site.register(Marks)
@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)

from .models import CompanySemesterInfo

@admin.register(CompanySemesterInfo)
class CompanySemesterInfoAdmin(admin.ModelAdmin):
    list_display = ('company', 'semester', 'total_seats', 'seats_taken')
    list_filter = ('semester', 'company')
    search_fields = ('company__name', 'semester__name')


from django.contrib import admin
from .models import InternshipSelection

@admin.register(InternshipSelection)
class InternshipSelectionAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester', 'company', 'self_managed_company_name', 'selected_at')
    list_filter = ('semester',)
    search_fields = ('student__student_id', 'student__name', 'company__name', 'self_managed_company_name')

