import io
import zipfile
from xml.sax.saxutils import escape
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import redirect
from .models import ServiceCategory, MedicalService, InsuranceProvider, InsuranceTariff, Practitioner, PractitionerGroup
from .forms import CategoryForm, ServiceForm, InsuranceForm, TariffForm, PractitionerForm, PractitionerGroupForm
from .importer import import_imaging_services, import_services, import_tariffs
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
                if kind == 'imaging':
                    created, updated, errors = import_imaging_services(upload)
                elif kind == 'services':
                    created, updated, errors = import_services(upload)
                else:
                    created, updated, errors = import_tariffs(upload)
                if errors:
                    messages.error(request, 'به‌دلیل خطا در فایل، هیچ موردی ثبت یا به‌روزرسانی نشد.')
                    for error in errors: messages.error(request, error)
                else:
                    messages.success(request, f'{created} مورد جدید ثبت و {updated} مورد به‌روزرسانی شد.')
            except ValueError as exc: messages.error(request, str(exc))
        return redirect('definition_import')
    return render(request, 'definitions/import.html')


def import_template(request, kind):
    if kind == 'imaging':
        headers = ['گروه خدمت', 'کد داخلی', 'کد استاندارد', 'نام خدمت', 'تعرفه آزاد']
    elif kind == 'services':
        headers = ['دسته', 'کد داخلی', 'کد استاندارد', 'نام خدمت', 'تعرفه آزاد']
    else:
        headers = ['کد خدمت', 'سازمان بیمه', 'نام بیمه', 'سهم بیمار', 'سهم بیمه', 'سهم بیمه تکمیلی']
    def column_name(index):
        name = ''
        while index:
            index, remainder = divmod(index - 1, 26)
            name = chr(65 + remainder) + name
        return name
    cells = ''.join(f'<c r="{column_name(index)}1" t="inlineStr"><is><t>{escape(header)}</t></is></c>' for index, header in enumerate(headers, 1))
    sheet = f'<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1">{cells}</row></sheetData></worksheet>'
    files = {
        '[Content_Types].xml': '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>',
        '_rels/.rels': '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        'xl/workbook.xml': '<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="تعرفه‌ها" sheetId="1" r:id="rId1"/></sheets></workbook>',
        'xl/_rels/workbook.xml.rels': '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>',
        'xl/worksheets/sheet1.xml': sheet,
    }
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as book:
        for filename, content in files.items():
            book.writestr(filename, content.encode('utf-8'))
    response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="darman-soft-{kind}-template.xlsx"'
    return response

# Create your views here.
