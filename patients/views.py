from django.shortcuts import render
from django.shortcuts import redirect
from .forms import PatientForm
from .models import Patient


def patient_list(request):
    form = PatientForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('patient_list')
    return render(request, 'patients/list.html', {'form': form, 'patients': Patient.objects.all()})

# Create your views here.
