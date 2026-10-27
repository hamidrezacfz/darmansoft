from django import forms
from .models import ServiceCategory, MedicalService, InsuranceProvider, InsuranceTariff, Practitioner, PractitionerGroup
class CategoryForm(forms.ModelForm):
    class Meta: model = ServiceCategory; fields = ['name']
class ServiceForm(forms.ModelForm):
    class Meta: model = MedicalService; fields = ['category','code','standard_code','name','base_price','active']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = ServiceCategory.objects.exclude(name__startswith='دندانپزشکی - ')
class InsuranceForm(forms.ModelForm):
    class Meta: model = InsuranceProvider; fields = ['organization','name','active']
class TariffForm(forms.ModelForm):
    class Meta: model = InsuranceTariff; fields = ['service','insurance','patient_share','insurer_share','supplementary_share']
class PractitionerGroupForm(forms.ModelForm):
    class Meta: model = PractitionerGroup; fields = ['name','active']
class PractitionerForm(forms.ModelForm):
    class Meta: model = Practitioner; fields = ['name','medical_system_code','group','role','share_percent','active']
    def clean_medical_system_code(self):
        return self.cleaned_data['medical_system_code'].strip() or None
