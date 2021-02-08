from django import forms
from .models import *

class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        exclude = []
        localized_fields = '__all__'

class NurseForm(forms.ModelForm):
    class Meta:
        model = Nurse
        exclude = []
        localized_fields = '__all__'

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        exclude = []
        localized_fields = '__all__'

class SiteManagerForm(forms.ModelForm):
    class Meta:
        model = SiteManager
        exclude = []
        localized_fields = '__all__'