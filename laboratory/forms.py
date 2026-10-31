from django import forms
from django.db.models import Q
from definitions.models import MedicalService, Practitioner
from .models import LaboratoryOrderTest

class PractitionerLookupWidget(forms.TextInput):
    def render(self,name,value,attrs=None,renderer=None):
        code=super().render(name,value,attrs,renderer)
        return code+'<input name="referring_practitioner_name" id="id_referring_practitioner_name" placeholder="اگر کد در فهرست نبود، نام پزشک را وارد کنید">'

class LaboratoryOrderForm(forms.Form):
    national_id=forms.CharField(label='کد ملی',max_length=10); first_name=forms.CharField(label='نام',max_length=50); last_name=forms.CharField(label='نام خانوادگی',max_length=70); mobile=forms.CharField(label='شماره همراه',max_length=15,required=False)
    tests=forms.ModelMultipleChoiceField(label='آزمایش‌ها',queryset=MedicalService.objects.none(),widget=forms.SelectMultiple(attrs={'size':8}))
    practitioner=forms.CharField(label='کد نظام پزشکی ارجاع‌دهنده یا نام پزشک',max_length=120,required=False,widget=PractitionerLookupWidget()); priority=forms.ChoiceField(label='اولویت',choices=[('normal','عادی'),('urgent','فوری'),('emergency','اورژانسی')]); notes=forms.CharField(label='توضیحات',required=False,widget=forms.Textarea(attrs={'rows':2}))
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs); self.fields['tests'].queryset=MedicalService.objects.filter(active=True,category__panel='laboratory').select_related('category').order_by('category__name','name'); self.fields['practitioner'].queryset=Practitioner.objects.filter(active=True).filter(Q(active_panels__contains=['laboratory'])|Q(active_panels=[])).order_by('name')

class ResultForm(forms.ModelForm):
    class Meta:
        model=LaboratoryOrderTest; fields=('result','unit','reference_range','flag')
