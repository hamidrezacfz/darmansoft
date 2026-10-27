from django import forms
from .models import MedicalRecord
class MedicalRecordForm(forms.ModelForm):
    class Meta: model=MedicalRecord; fields=['patient','complaint','diagnosis','notes']
