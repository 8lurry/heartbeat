from django import forms
from .models import Schedule, Token, HistoricalRecord

class HistoricalRecordForm(forms.ModelForm):
    class Meta:
        model = HistoricalRecord
        exclude = []
        localized_fields = "__all__"

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        exclude = []
        localized_fields = "__all__"

class TokenForm(forms.ModelForm):
    class Meta:
        model = Token
        exclude = []
        localized_fields = "__all__"