from django import forms
from .models import Admission
from definitions.models import MedicalService, Practitioner, InsuranceProvider

class AdmissionForm(forms.Form):
    national_id = forms.CharField(label='کد ملی', max_length=10)
    first_name = forms.CharField(label='نام', max_length=50)
    last_name = forms.CharField(label='نام خانوادگی', max_length=70)
    mobile = forms.CharField(label='شماره همراه', max_length=15, required=False)
    service_code = forms.CharField(label='کد خدمت', max_length=20,)
    practitioner_code = forms.CharField(label='کد نظام پزشکی / پرسنلی', max_length=30, required=False)
    practitioner = forms.ModelChoiceField(label='پزشک یا انجام‌دهنده', queryset=Admission._meta.get_field('practitioner').remote_field.model.objects.filter(active=True))
    insurance = forms.ModelChoiceField(label='بیمه', queryset=Admission._meta.get_field('insurance').remote_field.model.objects.filter(active=True), required=False)
    patient_share = forms.DecimalField(label='مبلغ پرداخت بیمار (ریال)', max_digits=12, decimal_places=0)
    insurer_share = forms.DecimalField(label='مبلغ سهم بیمه (ریال)', max_digits=12, decimal_places=0, required=False, initial=0)
    supplementary_share = forms.DecimalField(label='مبلغ سهم بیمه تکمیلی (ریال)', max_digits=12, decimal_places=0, required=False, initial=0)


class OpenAdmissionEditForm(forms.Form):
    first_name = forms.CharField(label='نام', max_length=50)
    last_name = forms.CharField(label='نام خانوادگی', max_length=70)
    mobile = forms.CharField(label='شماره همراه', max_length=15, required=False)
    service = forms.ModelChoiceField(label='خدمت', queryset=MedicalService.objects.filter(active=True))
    practitioner = forms.ModelChoiceField(label='پزشک یا انجام‌دهنده', queryset=Practitioner.objects.filter(active=True), required=False)
    insurance = forms.ModelChoiceField(label='بیمه', queryset=InsuranceProvider.objects.filter(active=True), required=False)
    patient_share = forms.DecimalField(label='مبلغ پرداخت بیمار (ریال)', max_digits=12, decimal_places=0)
    insurer_share = forms.DecimalField(label='مبلغ سهم بیمه (ریال)', max_digits=12, decimal_places=0, required=False)
    supplementary_share = forms.DecimalField(label='مبلغ سهم بیمه تکمیلی (ریال)', max_digits=12, decimal_places=0, required=False)
