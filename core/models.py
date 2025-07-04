from django.db import models
from django.contrib.auth.models import User



from django.contrib.auth.models import User
from django.db import models

class Semester(models.Model):
    name = models.CharField(max_length=50)  # e.g. "Summer 2025"
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_active:
            # Deactivate other semesters
            Semester.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=255)
    total_seats = models.PositiveIntegerField()
    seats_taken = models.PositiveIntegerField(default=0)
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    def seats_available(self):
        return self.total_seats - self.seats_taken


class AcademicSupervisor(models.Model):
    # Faculty username from university system
    faculty_username = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True, null=True)
    designation = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.faculty_username})"


class IndustrialSupervisor(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True, null=True)
    designation = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name




    # ...

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Basic student info
    student_id = models.CharField(max_length=50, unique=True)  # university student ID
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50)
    address = models.TextField(blank=True)
    skills = models.TextField(blank=True)  # comma separated or JSON string if you want
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True)

    # Relations
    academic_supervisor = models.ForeignKey(AcademicSupervisor, on_delete=models.SET_NULL, null=True, blank=True)
    industrial_supervisor = models.ForeignKey(IndustrialSupervisor, on_delete=models.SET_NULL, null=True, blank=True)

    # Self-managed internship info (if student managed company themselves)
    def __str__(self):
        return f"{self.student_id} - {self.name}"


class Marks(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True)
    academic_marks = models.PositiveIntegerField(null=True, blank=True)  # out of 30
    industrial_marks = models.PositiveIntegerField(null=True, blank=True)  # out of 30
    board_marks = models.PositiveIntegerField(null=True, blank=True)  # out of 40 (if applicable)

    def __str__(self):
        return f"Marks for {self.student.student_id}"


class CompanySemesterInfo(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    total_seats = models.PositiveIntegerField()
    seats_taken = models.PositiveIntegerField(default=0)


class InternshipSelection(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    company = models.ForeignKey('Company', on_delete=models.SET_NULL, null=True, blank=True)

    self_managed_company_name = models.CharField(max_length=255, blank=True, null=True)
    self_managed_company_details = models.TextField(blank=True, null=True)

    selected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'semester')  # One selection per student per semester

    def __str__(self):
        return f"{self.student.student_id} - {self.semester.name} - {self.company or self.self_managed_company_name}"
