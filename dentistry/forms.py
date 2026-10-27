from django import forms
from definitions.models import InsuranceProvider, InsuranceTariff, MedicalService, Practitioner, ServiceCategory


class DentalServiceForm(forms.Form):
    group = forms.ModelChoiceField(label='گروه خدمت', queryset=ServiceCategory.objects.none())
    code = forms.CharField(label='کد داخلی خدمت', max_length=20)
    standard_code = forms.CharField(label='کد استاندارد (اختیاری)', max_length=30, required=False)
    name = forms.CharField(label='نام تست / خدمت دندانپزشکی', max_length=120)
    tooth_scope = forms.CharField(label='شماره / ناحیه دندان', max_length=100, required=False)
    base_price = forms.DecimalField(label='تعرفه آزاد (ریال)', min_value=0, decimal_places=0, max_digits=12, initial=0)
    def __init__(self, *args, groups=None, **kwargs):
        super().__init__(*args, **kwargs); self.fields['group'].queryset = groups if groups is not None else ServiceCategory.objects.none()
    def clean_code(self):
        code = self.cleaned_data['code'].strip()
        if MedicalService.objects.filter(code=code).exists(): raise forms.ValidationError('این کد داخلی قبلاً ثبت شده است.')
        return code


class GroupPriceForm(forms.Form):
    group = forms.ModelChoiceField(label='گروه خدمت', queryset=ServiceCategory.objects.none())
    base_price = forms.DecimalField(label='تعرفه آزاد هر خدمت در گروه (ریال)', min_value=0, decimal_places=0, max_digits=12)
    def __init__(self, *args, groups=None, **kwargs):
        super().__init__(*args, **kwargs); self.fields['group'].queryset = groups if groups is not None else ServiceCategory.objects.none()


class DentalTariffForm(forms.ModelForm):
    service = forms.ModelChoiceField(label='خدمت دندانپزشکی', queryset=MedicalService.objects.none())
    insurance = forms.ModelChoiceField(label='بیمه', queryset=InsuranceProvider.objects.filter(active=True))
    class Meta:
        model = InsuranceTariff
        fields = ['service', 'insurance', 'patient_share', 'insurer_share', 'supplementary_share']
    def __init__(self, *args, services=None, **kwargs):
        super().__init__(*args, **kwargs); self.fields['service'].queryset = services if services is not None else MedicalService.objects.none()


class DentalAdmissionForm(forms.Form):
    national_id = forms.CharField(label='کد ملی', max_length=10)
    first_name = forms.CharField(label='نام', max_length=50)
    last_name = forms.CharField(label='نام خانوادگی', max_length=70)
    mobile = forms.CharField(label='شماره همراه', max_length=15, required=False)
    service = forms.ModelChoiceField(label='خدمت دندانپزشکی', queryset=MedicalService.objects.none())
    practitioner = forms.ModelChoiceField(label='دندان‌پزشک / انجام‌دهنده', queryset=Practitioner.objects.filter(active=True), required=False)
    tooth_numbers = forms.CharField(required=False, widget=forms.HiddenInput())
    note = forms.CharField(label='توضیحات', required=False, widget=forms.Textarea(attrs={'rows': 2}))
    def __init__(self, *args, services=None, **kwargs):
        super().__init__(*args, **kwargs); self.fields['service'].queryset = services if services is not None else MedicalService.objects.none()
