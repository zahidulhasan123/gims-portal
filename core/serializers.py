# core/serializers.py
from rest_framework import serializers
from .models import Student, Company, AcademicSupervisor, IndustrialSupervisor, Marks

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class AcademicSupervisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicSupervisor
        fields = '__all__'

class IndustrialSupervisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndustrialSupervisor
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    industrial_supervisor = IndustrialSupervisorSerializer(read_only=True)

    class Meta:
        model = Student
        exclude = ['user']  # or include all if preferred

class MarksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marks
        fields = '__all__'
