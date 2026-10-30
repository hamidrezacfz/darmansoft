from django import forms

from definitions.models import InsuranceProvider, MedicalService, Practitioner, ServiceCategory


IMAGING_GROUPS = ('تصویربرداری', 'سی تی اسکن', 'سونوگرافی', 'MRI')


class ImagingServiceChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, service):
        return f'{service.category.name} — {service.name}'


class ImagingAdmissionForm(forms.Form):
    national_id = forms.CharField(label='کد ملی', max_length=10)
    first_name = forms.CharField(label='نام', max_length=50)
    last_name = forms.CharField(label='نام خانوادگی', max_length=70)
    mobile = forms.CharField(label='شماره همراه', max_length=15, required=False)
    group = forms.ModelChoiceField(label='گروه خدمت تصویربرداری', queryset=ServiceCategory.objects.none(), empty_label='انتخاب گروه')
    service = ImagingServiceChoiceField(label='خدمت', queryset=MedicalService.objects.none(), empty_label='انتخاب خدمت')
    practitioner = forms.ModelChoiceField(label='پزشک / کارشناس انجام‌دهنده', queryset=Practitioner.objects.filter(active=True), required=False, empty_label='انتخاب انجام‌دهنده')
    insurance = forms.ModelChoiceField(label='بیمه', queryset=InsuranceProvider.objects.filter(active=True), required=False, empty_label='بدون بیمه')
    patient_share = forms.DecimalField(label='مبلغ پرداخت بیمار (ریال)', max_digits=12, decimal_places=0)
    insurer_share = forms.DecimalField(label='مبلغ سهم بیمه (ریال)', max_digits=12, decimal_places=0, required=False, initial=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        groups = ServiceCategory.objects.filter(panel=ServiceCategory.Panel.IMAGING).order_by('name')
        self.fields['group'].queryset = groups
        self.fields['service'].queryset = MedicalService.objects.filter(active=True, category__in=groups).select_related('category').order_by('category__name', 'name')

    def clean(self):
        cleaned = super().clean()
        group = cleaned.get('group')
        service = cleaned.get('service')
        if group and service and service.category_id != group.id:
            self.add_error('service', 'خدمت انتخاب‌شده متعلق به گروه انتخابی نیست.')
        return cleaned
