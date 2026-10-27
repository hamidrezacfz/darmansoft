from django import forms
from definitions.models import MedicalService, Practitioner, ServiceCategory
from .models import Appointment, WorkSchedule

class JalaliDateTimeField(forms.DateTimeField):
    def prepare_value(self, value):
        if value:
            from core.jalali import to_jalali
            return to_jalali(value, with_time=True)
        return value
    def to_python(self, value):
        if not value: return None
        from core.jalali import from_jalali_datetime
        try: return from_jalali_datetime(value)
        except (TypeError, ValueError): raise forms.ValidationError('تاریخ و ساعت را به شکل ۱۴۰۵/۰۷/۲۵ ۱۰:۳۰ وارد کنید.')

class AppointmentBookingForm(forms.Form):
    class Department:
        RECEPTION = 'reception'
        BEAUTY = 'beauty'
        DENTISTRY = 'dentistry'

    national_id = forms.CharField(label='کد ملی بیمار', max_length=10, widget=forms.TextInput(attrs={'inputmode':'numeric','placeholder':'۰۰۱۲۳۴۵۶۷۸'}))
    first_name = forms.CharField(label='نام بیمار', max_length=50)
    last_name = forms.CharField(label='نام خانوادگی بیمار', max_length=70)
    mobile = forms.CharField(label='شماره تماس', max_length=15, required=False, widget=forms.TextInput(attrs={'inputmode':'tel','placeholder':'۰۹۱۲...'}))
    department = forms.ChoiceField(label='بخش نوبت', choices=(), widget=forms.Select())
    service = forms.ModelChoiceField(queryset=MedicalService.objects.filter(active=True), required=False, widget=forms.HiddenInput())
    practitioner = forms.ModelChoiceField(label='پزشک / اپراتور / انجام‌دهنده', queryset=Practitioner.objects.filter(active=True), empty_label='انتخاب انجام‌دهنده')
    appointment_date = forms.CharField(label='تاریخ نوبت', widget=forms.TextInput(attrs={'readonly': 'readonly', 'placeholder':'انتخاب از تقویم شمسی'}))
    appointment_time = forms.TimeField(label='ساعت نوبت', widget=forms.TimeInput(attrs={'type':'time'}))
    reminder_requested = forms.BooleanField(label='یادآوری پیامکی', required=False)
    note = forms.CharField(label='یادداشت', required=False, max_length=200, widget=forms.Textarea(attrs={'rows':2,'placeholder':'توضیحات یا علت مراجعه'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        active_services = MedicalService.objects.filter(active=True)
        choices = [('', 'انتخاب بخش')]
        if active_services.exclude(category__name__startswith='دندانپزشکی').exclude(category__name__icontains='زیبایی').exists():
            choices.append((self.Department.RECEPTION, 'پذیرش'))
        if active_services.filter(category__name__icontains='زیبایی').exists():
            choices.append((self.Department.BEAUTY, 'زیبایی'))
        if active_services.filter(category__name__startswith='دندانپزشکی').exists():
            choices.append((self.Department.DENTISTRY, 'دندان‌پزشکی'))
        self.fields['department'].choices = choices
    def clean_national_id(self):
        value = self.cleaned_data['national_id'].strip().replace('-', '')
        if not value.isdigit() or len(value) != 10: raise forms.ValidationError('کد ملی باید ۱۰ رقم باشد.')
        return value

    def clean(self):
        cleaned = super().clean()
        department = cleaned.get('department')
        if department:
            services = MedicalService.objects.filter(active=True)
            if department == self.Department.DENTISTRY:
                services = services.filter(category__name__startswith='دندانپزشکی')
            elif department == self.Department.BEAUTY:
                services = services.filter(category__name__icontains='زیبایی')
            else:
                services = services.exclude(category__name__startswith='دندانپزشکی').exclude(category__name__icontains='زیبایی')
            service = services.select_related('category').order_by('id').first()
            if not service:
                self.add_error('department', 'برای این بخش خدمت فعالی تعریف نشده است.')
            else:
                cleaned['service'] = service
        if cleaned.get('appointment_date') and cleaned.get('appointment_time'):
            from core.jalali import from_jalali_datetime
            cleaned['appointment_at'] = from_jalali_datetime(f"{cleaned['appointment_date']} {cleaned['appointment_time'].strftime('%H:%M')}")
        return cleaned


class WorkScheduleForm(forms.ModelForm):
    class Meta:
        model = WorkSchedule
        fields = ['practitioner', 'department', 'weekday', 'start_time', 'end_time', 'active']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned = super().clean()
        practitioner = cleaned.get('practitioner')
        department = cleaned.get('department')
        start_time = cleaned.get('start_time')
        end_time = cleaned.get('end_time')
        if bool(practitioner) == bool(department):
            raise forms.ValidationError('دقیقاً پزشک/انجام‌دهنده یا یک بخش را انتخاب کنید.')
        if start_time and end_time and start_time >= end_time:
            self.add_error('end_time', 'ساعت پایان باید بعد از ساعت شروع باشد.')
        return cleaned
