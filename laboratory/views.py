from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404,redirect,render
from django.utils import timezone
from patients.models import Patient
from reception.models import Admission
from .forms import LaboratoryOrderForm,ResultForm
from .models import LaboratoryOrder,LaboratoryOrderTest,LaboratorySpecimen,LaboratoryReferenceRange,LaboratoryWorklist

def patient_lookup(request):
    p=Patient.objects.filter(national_id=request.GET.get('national_id','').strip()).first(); return JsonResponse({'found':bool(p),'first_name':p.first_name if p else '','last_name':p.last_name if p else '','mobile':p.mobile if p else ''})
def index(request):
    form=LaboratoryOrderForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        d=form.cleaned_data; patient,_=Patient.objects.update_or_create(national_id=d['national_id'],defaults={'first_name':d['first_name'],'last_name':d['last_name'],'mobile':d['mobile']}); practitioner=None
        if d['practitioner']:
            practitioner=__import__('definitions.models',fromlist=['Practitioner']).Practitioner.objects.filter(medical_system_code=d['practitioner'],active=True).first()
        referring_name=request.POST.get('referring_practitioner_name','').strip() or (str(practitioner) if practitioner else '')
        last=LaboratoryOrder.objects.order_by('-id').first(); n=int(last.accession_number[3:])+1 if last and last.accession_number.startswith('LAB') and last.accession_number[3:].isdigit() else 1; code=f'LAB{n:06d}'
        with transaction.atomic():
            order=LaboratoryOrder.objects.create(patient=patient,practitioner=practitioner,referring_practitioner_name=referring_name,accession_number=code,priority=d['priority'],notes=d['notes'],created_by=request.user if request.user.is_authenticated else None); LaboratorySpecimen.objects.create(order=order,specimen_type='ثبت‌نشده',barcode=f'{code}-01')
            for service in d['tests']:
                admission=Admission.objects.create(patient=patient,service=service,practitioner=practitioner,practitioner_name=referring_name,patient_share=service.base_price,insurer_share=0,tracking_code=f'{code}-{service.pk}',created_by=request.user if request.user.is_authenticated else None); LaboratoryOrderTest.objects.create(order=order,service=service,admission=admission)
        return redirect(f'/laboratory/?ref={code}')
    return render(request,'laboratory/index.html',{'form':form,'orders':LaboratoryOrder.objects.select_related('patient').prefetch_related('tests__service')[:20],'referral_code':request.GET.get('ref','')})
def order_detail(request,pk):
    order=get_object_or_404(LaboratoryOrder.objects.prefetch_related('tests__service','specimens'),pk=pk)
    if request.method=='POST':
        for test in order.tests.all():
            f=ResultForm(request.POST,instance=test,prefix=f'test-{test.pk}')
            if f.is_valid(): obj=f.save(commit=False); obj.result_status='entered'; obj.save()
        order.status='in_process'; order.save(update_fields=['status']); messages.success(request,'نتایج آزمایش ذخیره شد.'); return redirect('laboratory_order_detail',pk=pk)
    return render(request,'laboratory/detail.html',{'order':order,'result_forms':[(t,ResultForm(instance=t,prefix=f'test-{t.pk}')) for t in order.tests.all()]})
def verify_order(request,pk):
    order=get_object_or_404(LaboratoryOrder,pk=pk)
    if request.method=='POST': order.tests.update(result_status='verified',verified_by=request.user if request.user.is_authenticated else None,verified_at=timezone.now()); order.status='released'; order.save(update_fields=['status'])
    return redirect('laboratory_order_detail',pk=pk)

def definitions(request):
    ranges=LaboratoryReferenceRange.objects.select_related('service').filter(service__category__panel='laboratory').order_by('service__code')
    worklists=LaboratoryWorklist.objects.prefetch_related('services').order_by('name')
    return render(request,'laboratory/definitions.html',{'ranges':ranges,'worklists':worklists})
