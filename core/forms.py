from django import forms
from .models import Student

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ['user', 'email','company', 'industrial_supervisor', 'academic_supervisor','self_managed_company_details','self_managed_company_name','has_selected_company','semester']
