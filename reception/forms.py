from django import forms
from django.db.models import Q
from django.utils.safestring import mark_safe
from .models import Admission
from definitions.models import MedicalService, Practitioner, InsuranceProvider, ServiceCategory

def practitioners_for_panel(panel):
    return Practitioner.objects.filter(active=True).filter(Q(active_panels__contains=[panel]) | Q(active_panels=[])).order_by('name')


class ServiceSearchWidget(forms.TextInput):
    def render(self, name, value, attrs=None, renderer=None):
        field = super().render(name, value, attrs, renderer)
        return mark_safe(field + '<datalist id="service-suggestions"></datalist><script>(function(){const i=document.getElementById("id_service_code"),l=document.getElementById("service-suggestions"),ins=document.getElementById("id_insurance");if(!i||!l)return;i.setAttribute("list","service-suggestions");let t;i.addEventListener("input",()=>{clearTimeout(t);const q=i.value.trim();if(q.length<2){l.innerHTML="";return}t=setTimeout(async()=>{const d=await (await fetch("/reception/service-lookup/?q="+encodeURIComponent(q))).json();l.innerHTML=d.items.map(x=>"<option value=\\""+(x.code||x.name)+"\\">"+x.name+" — "+x.category+"</option>").join("");if(d.items.length===1&&((d.items[0].code||d.items[0].name).toLowerCase()===q.toLowerCase()))price()},180)});async function price(){if(!i.value)return;const d=await (await fetch("/reception/tariff-preview/?service_code="+encodeURIComponent(i.value)+"&insurance="+(ins?ins.value:""))).json();if(!d.found)return;const p=document.getElementById("id_patient_share"),o=document.getElementById("id_insurer_share"),s=document.getElementById("id_supplementary_share");if(p)p.value=d.patient_share;if(o)o.value=d.insurer_share;if(s)s.value=d.supplementary_share}i.addEventListener("change",price);if(ins)ins.addEventListener("change",price)})()</script>')

class AdmissionForm(forms.Form):
    national_id = forms.CharField(label='کد ملی', max_length=10)
    first_name = forms.CharField(label='نام', max_length=50)
    last_name = forms.CharField(label='نام خانوادگی', max_length=70)
    mobile = forms.CharField(label='شماره همراه', max_length=15, required=False)
    service_code = forms.CharField(label='کد یا نام خدمت', max_length=120, widget=ServiceSearchWidget(attrs={'autocomplete': 'off'}))
    practitioner_code = forms.CharField(label='کد نظام پزشکی / پرسنلی', max_length=30, required=False)
    practitioner = forms.ModelChoiceField(label='پزشک یا انجام‌دهنده', queryset=practitioners_for_panel(ServiceCategory.Panel.GENERAL))
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
