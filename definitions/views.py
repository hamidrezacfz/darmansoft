import csv
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import redirect
from .models import ServiceCategory, MedicalService, InsuranceProvider, InsuranceTariff, Practitioner, PractitionerGroup
from .forms import CategoryForm, ServiceForm, InsuranceForm, TariffForm, PractitionerForm, PractitionerGroupForm
from .importer import import_services, import_tariffs
FORMS = {'category': CategoryForm, 'service': ServiceForm, 'insurance': InsuranceForm, 'tariff': TariffForm, 'practitioner_groups': PractitionerGroupForm}
def practitioners(request):
    form = PractitionerForm(request.POST or None)
    if request.method == 'POST' and form.is_valid(): form.save(); return redirect('practitioners')
    return render(request, 'definitions/practitioners.html', {'form': form, 'practitioners': Practitioner.objects.select_related('group')})

def setup(request, kind):
    options = {'categories': ('دسته‌های خدمت', CategoryForm, ServiceCategory), 'services': ('خدمات پزشکی', ServiceForm, MedicalService), 'insurances': ('بیمه‌ها', InsuranceForm, InsuranceProvider), 'tariffs': ('تعرفه‌های بیمه', TariffForm, InsuranceTariff), 'practitioner-groups': ('گروه‌های پزشکان و پرسنل', PractitionerGroupForm, PractitionerGroup)}
    if kind not in options: return redirect('definitions')
    title, form_class, model = options[kind]
    form = form_class(request.POST or None)
    if request.method == 'POST' and form.is_valid(): form.save(); return redirect('definition_setup', kind=kind)
    items = model.objects.all()
    if kind == 'services': items = items.exclude(category__name__startswith='دندانپزشکی - ')
    if kind == 'categories': items = items.exclude(name__startswith='دندانپزشکی - ')
    return render(request, 'definitions/setup.html', {'title': title, 'form': form, 'items': items})
def index(request):
    form_type = request.POST.get('form_type')
    if request.method == 'POST' and form_type in FORMS:
        form = FORMS[form_type](request.POST)
        if form.is_valid(): form.save(); return redirect('definitions')
    return render(request, 'definitions/index.html', {'category_form': CategoryForm(), 'service_form': ServiceForm(), 'insurance_form': InsuranceForm(), 'tariff_form': TariffForm(), 'categories': ServiceCategory.objects.exclude(name__startswith='دندانپزشکی - '), 'services': MedicalService.objects.select_related('category').exclude(category__name__startswith='دندانپزشکی - '), 'insurances': InsuranceProvider.objects.all(), 'tariffs': InsuranceTariff.objects.select_related('service','insurance').exclude(service__category__name__startswith='دندانپزشکی - ')})


def import_file(request):
    if request.method == 'POST':
        upload = request.FILES.get('spreadsheet')
        kind = request.POST.get('kind')
        if not upload:
            messages.error(request, 'ابتدا فایل را انتخاب کنید.')
        else:
            try:
                created, updated, errors = import_services(upload) if kind == 'services' else import_tariffs(upload)
                messages.success(request, f'{created} مورد جدید ثبت و {updated} مورد به‌روزرسانی شد.')
                for error in errors[:8]: messages.error(request, error)
            except ValueError as exc: messages.error(request, str(exc))
        return redirect('definition_import')
    return render(request, 'definitions/import.html')


def import_template(request, kind):
    headers = ['دسته', 'کد داخلی', 'کد استاندارد', 'نام خدمت', 'تعرفه آزاد'] if kind == 'services' else ['کد خدمت', 'سازمان بیمه', 'نام بیمه', 'سهم بیمار', 'سهم بیمه', 'سهم بیمه تکمیلی']
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="darman-soft-{kind}-template.csv"'
    response.write('\ufeff'); csv.writer(response).writerow(headers)
    return response

# Create your views here.
