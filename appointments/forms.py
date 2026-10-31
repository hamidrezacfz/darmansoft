from django import forms
from django.utils.safestring import mark_safe
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


class SlotTimeWidget(forms.TimeInput):
    def render(self, name, value, attrs=None, renderer=None):
        field = super().render(name, value, attrs, renderer)
        script = '<div id="appointment-slots" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(68px,1fr));width:100%;max-width:100%;gap:6px;margin:6px 0;overflow:hidden"></div><script>(function(){const d=document.getElementById("id_appointment_date"),p=document.getElementById("id_practitioner"),t=document.getElementById("id_appointment_time"),g=document.getElementById("appointment-slots");if(!d||!p||!t||!g)return;let last="";async function load(){const key=d.value+"|"+p.value;if(key===last)return;last=key;if(!d.value||!p.value){g.innerHTML="";return}const x=await (await fetch("/appointments/availability/?date="+encodeURIComponent(d.value)+"&practitioner="+p.value)).json();g.innerHTML=x.slots.length?x.slots.map(s=>"<button type=\\"button\\" style=\\"min-width:0;width:100%;padding:6px 3px;border:1px solid #ccdada;border-radius:7px;background:"+(s.available?"#fff":"#dbe1e1")+";color:"+(s.available?"#18323a":"#999")+";font-size:11px;overflow:hidden\\" "+(s.available?"":"disabled")+">"+s.time+"<small style=\\"display:block;white-space:nowrap\\">"+s.label+"</small></button>").join(""):"<span style=\\"color:#9a6a18;grid-column:1/-1\\">برای این پزشک و تاریخ شیفت فعالی ثبت نشده است.</span>";g.querySelectorAll("button:not([disabled])").forEach(b=>b.onclick=()=>{t.value=b.textContent.trim().slice(0,5);g.querySelectorAll("button").forEach(z=>z.style.background="#fff");b.style.background="#bde8dc"})}d.addEventListener("change",load);p.addEventListener("change",load);setInterval(load,400);load()})()</script>'
        return mark_safe(field + script)

class AppointmentBookingForm(forms.Form):
    class Department:
        RECEPTION = 'reception'
        BEAUTY = 'beauty'
        DENTISTRY = 'dentistry'
        IMAGING = 'imaging'
        LABORATORY = 'laboratory'
        PHYSIOTHERAPY = 'physiotherapy'
        PHARMACY = 'pharmacy'

    national_id = forms.CharField(label='کد ملی بیمار', max_length=10, widget=forms.TextInput(attrs={'inputmode':'numeric','placeholder':'۰۰۱۲۳۴۵۶۷۸'}))
    first_name = forms.CharField(label='نام بیمار', max_length=50)
    last_name = forms.CharField(label='نام خانوادگی بیمار', max_length=70)
    mobile = forms.CharField(label='شماره تماس', max_length=15, required=False, widget=forms.TextInput(attrs={'inputmode':'tel','placeholder':'۰۹۱۲...'}))
    department = forms.ChoiceField(label='بخش نوبت', choices=(), widget=forms.Select())
    service = forms.ModelChoiceField(queryset=MedicalService.objects.filter(active=True), required=False, widget=forms.HiddenInput())
    practitioner = forms.ModelChoiceField(label='پزشک / اپراتور / انجام‌دهنده', queryset=Practitioner.objects.filter(active=True), empty_label='انتخاب انجام‌دهنده')
    appointment_date = forms.CharField(label='تاریخ نوبت', widget=forms.TextInput(attrs={'readonly': 'readonly', 'placeholder':'انتخاب از تقویم شمسی'}))
    appointment_time = forms.TimeField(label='ساعت نوبت', widget=SlotTimeWidget(attrs={'type':'time'}))
    reminder_requested = forms.BooleanField(label='یادآوری پیامکی', required=False)
    note = forms.CharField(label='یادداشت', required=False, max_length=200, widget=forms.Textarea(attrs={'rows':2,'placeholder':'توضیحات یا علت مراجعه'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        active_services = MedicalService.objects.filter(active=True)
        choices = [('', 'انتخاب بخش')]
        panel_choices = [(self.Department.RECEPTION, ServiceCategory.Panel.GENERAL, 'پذیرش'), (self.Department.BEAUTY, ServiceCategory.Panel.AESTHETICS, 'زیبایی و سلامت'), (self.Department.DENTISTRY, ServiceCategory.Panel.DENTISTRY, 'دندان‌پزشکی'), (self.Department.IMAGING, ServiceCategory.Panel.IMAGING, 'تصویربرداری'), (self.Department.LABORATORY, ServiceCategory.Panel.LABORATORY, 'آزمایشگاه'), (self.Department.PHYSIOTHERAPY, ServiceCategory.Panel.PHYSIOTHERAPY, 'فیزیوتراپی'), (self.Department.PHARMACY, ServiceCategory.Panel.PHARMACY, 'داروخانه')]
        for value, panel, label in panel_choices:
            choices.append((value, label))
        self.fields['department'].choices = choices
    def clean_national_id(self):
        value = self.cleaned_data['national_id'].strip().replace('-', '')
        if not value.isdigit() or len(value) != 10: raise forms.ValidationError('کد ملی باید ۱۰ رقم باشد.')
        return value

    def clean(self):
        cleaned = super().clean()
        department = cleaned.get('department')
        if department:
            panel_map = {self.Department.RECEPTION: ServiceCategory.Panel.GENERAL, self.Department.BEAUTY: ServiceCategory.Panel.AESTHETICS, self.Department.DENTISTRY: ServiceCategory.Panel.DENTISTRY, self.Department.IMAGING: ServiceCategory.Panel.IMAGING, self.Department.LABORATORY: ServiceCategory.Panel.LABORATORY, self.Department.PHYSIOTHERAPY: ServiceCategory.Panel.PHYSIOTHERAPY, self.Department.PHARMACY: ServiceCategory.Panel.PHARMACY}
            services = MedicalService.objects.filter(active=True, category__panel=panel_map.get(department, ServiceCategory.Panel.GENERAL))
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
    SHIFT_CHOICES = (('صبح', 'شیفت صبح'), ('عصر', 'شیفت عصر'), ('شب', 'شیفت شب'))
    start_date = forms.CharField(label='تاریخ شروع هفته شمسی', required=False, widget=forms.TextInput(attrs={'placeholder':'۱۴۰۵/۰۸/۱۰'}))
    end_date = forms.CharField(label='تاریخ پایان هفته شمسی', required=False, widget=forms.TextInput(attrs={'placeholder':'۱۴۰۵/۰۸/۱۶'}))
    weekdays = forms.MultipleChoiceField(label='روزهای فعال', choices=WorkSchedule.Weekday.choices, required=False, widget=forms.CheckboxSelectMultiple)
    shift_type = forms.ChoiceField(label='شیفت آماده', choices=SHIFT_CHOICES, required=False, initial='صبح')
    schedule_date = forms.CharField(required=False, widget=forms.HiddenInput())
    class Meta:
        model = WorkSchedule
        fields = ['practitioner', 'department', 'start_time', 'end_time', 'capacity', 'active']
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
        if not practitioner and not department:
            raise forms.ValidationError('حداقل پزشک/انجام‌دهنده یا یک بخش را انتخاب کنید.')
        if start_time and end_time and start_time >= end_time:
            self.add_error('end_time', 'ساعت پایان باید بعد از ساعت شروع باشد.')
        if cleaned.get('capacity', 0) < 1:
            self.add_error('capacity', 'ظرفیت باید حداقل ۱ نفر باشد.')
        if cleaned.get('schedule_date'):
            from core.jalali import from_jalali
            try:
                cleaned['schedule_date'] = from_jalali(cleaned['schedule_date'])
                cleaned['weekday'] = cleaned['schedule_date'].weekday()
            except (TypeError, ValueError):
                self.add_error('schedule_date', 'تاریخ را به شکل ۱۴۰۵/۰۸/۱۰ وارد کنید.')
        if cleaned.get('start_date') or cleaned.get('end_date'):
            from core.jalali import from_jalali
            try:
                start = from_jalali(cleaned.get('start_date')); end = from_jalali(cleaned.get('end_date'))
                if not start or not end or end < start: raise ValueError
                cleaned['range_start'], cleaned['range_end'] = start, end
            except (TypeError, ValueError):
                self.add_error('start_date', 'بازهٔ شروع و پایان را به شکل صحیح شمسی وارد کنید.')
            if not cleaned.get('weekdays'):
                self.add_error('weekdays', 'حداقل یک روز هفته را انتخاب کنید.')
        return cleaned
