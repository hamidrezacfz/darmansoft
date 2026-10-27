from django import forms

from definitions.models import MedicalService, Practitioner
from core.jalali import from_jalali

from .models import BeautyVisit


class BeautyVisitForm(forms.Form):
    national_id = forms.CharField(label='کد ملی', max_length=10)
    first_name = forms.CharField(label='نام', max_length=50)
    last_name = forms.CharField(label='نام خانوادگی', max_length=70)
    mobile = forms.CharField(label='شماره همراه', max_length=15, required=False)
    visit_type = forms.ChoiceField(label='نوع ثبت', choices=BeautyVisit.VisitType.choices)
    service = forms.ModelChoiceField(
        label='خدمت زیبایی، سلامت یا مراقبت',
        queryset=MedicalService.objects.filter(
            active=True,
            category__name__in=['زیبایی', 'سلامت'],
        ).select_related('category'),
        empty_label='انتخاب خدمت',
    )
    practitioner = forms.ModelChoiceField(label='انجام‌دهنده', queryset=Practitioner.objects.filter(active=True), required=False)
    treatment_area = forms.CharField(label='ناحیه / مورد خدمت', max_length=120, required=False, help_text='مثلاً صورت، پوست، مو یا مراقبت عمومی')
    notes = forms.CharField(label='توضیحات', required=False, widget=forms.Textarea(attrs={'rows': 3}))
    next_session_date = forms.CharField(label='تاریخ جلسه بعد', required=False, widget=forms.TextInput(attrs={'placeholder': 'انتخاب از تقویم شمسی', 'readonly': 'readonly'}))
    next_session_time = forms.TimeField(label='ساعت جلسه بعد', required=False, widget=forms.TimeInput(attrs={'type': 'time'}))

    def clean_next_session_date(self):
        value = self.cleaned_data['next_session_date']
        if not value:
            return None
        try:
            return from_jalali(value)
        except (TypeError, ValueError):
            raise forms.ValidationError('تاریخ را به‌صورت ۱۴۰۵/۰۷/۲۵ وارد کنید.')
