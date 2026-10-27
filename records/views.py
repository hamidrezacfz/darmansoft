from django.shortcuts import render
from django.shortcuts import redirect
from .forms import MedicalRecordForm
from .models import MedicalRecord
from django.shortcuts import get_object_or_404
from patients.models import Patient
from reception.models import Admission
from appointments.models import Appointment
from billing.models import Payment
def index(request):
    form=MedicalRecordForm(request.POST or None)
    if request.method=='POST' and form.is_valid(): form.save(); return redirect('records')
    return render(request,'records/index.html',{'form':form,'records':MedicalRecord.objects.select_related('patient')})

def patient_file(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    return render(request, 'records/patient_file.html', {
        'patient': patient,
        'records': MedicalRecord.objects.filter(patient=patient),
        'admissions': Admission.objects.filter(patient=patient).select_related('service', 'practitioner', 'insurance'),
        'appointments': Appointment.objects.filter(patient=patient).select_related('service', 'practitioner'),
        'payments': Payment.objects.filter(patient=patient).select_related('admission'),
    })

# Create your views here.
