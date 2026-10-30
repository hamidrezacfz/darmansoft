import io
import zipfile
from xml.sax.saxutils import escape
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.db import transaction
from django.db.models.deletion import ProtectedError
from .models import ServiceCategory, MedicalService, InsuranceProvider, InsuranceTariff, Practitioner, PractitionerGroup
from .forms import CategoryForm, ServiceForm, InsuranceForm, TariffForm, PractitionerForm, PractitionerGroupForm
from .importer import import_imaging_services, import_services, import_tariffs
FORMS = {'category': CategoryForm, 'service': ServiceForm, 'insurance': InsuranceForm, 'tariff': TariffForm, 'practitioner_groups': PractitionerGroupForm}
def practitioners(request):
    form = PractitionerForm(request.POST or None)
    if request.method == 'POST' and form.is_valid(): form.save(); return redirect('practitioners')
    return render(request, 'definitions/practitioners.html', {'form': form, 'practitioners': Practitioner.objects.select_related('group')})


DELETABLE_DEFINITIONS = {
    'categories': ServiceCategory,
    'services': MedicalService,
    'insurances': InsuranceProvider,
    'tariffs': InsuranceTariff,
    'practitioner-groups': PractitionerGroup,
    'practitioners': Practitioner,
}


def delete_definition(request, kind, pk):
    """Delete a base definition only when it isn't used by clinical records."""
    if request.method != 'POST' or kind not in DELETABLE_DEFINITIONS:
        return redirect('definitions')

    item = get_object_or_404(DELETABLE_DEFINITIONS[kind], pk=pk)
    try:
        item.delete()
        messages.success(request, 'مورد انتخاب‌شده حذف شد.')
    except ProtectedError:
        messages.error(
            request,
            'این مورد در پذیرش، نوبت‌دهی یا اطلاعات ثبت‌شده استفاده شده و برای حفظ سوابق قابل حذف نیست.',
        )
    target = 'practitioners' if kind == 'practitioners' else 'definition_setup'
    return redirect(target, **({} if kind == 'practitioners' else {'kind': kind}))

def setup(request, kind):
    options = {'categories': ('دسته‌های خدمت', CategoryForm, ServiceCategory), 'services': ('خدمات پزشکی', ServiceForm, MedicalService), 'insurances': ('بیمه‌ها', InsuranceForm, InsuranceProvider), 'tariffs': ('تعرفه‌های بیمه', TariffForm, InsuranceTariff), 'practitioner-groups': ('گروه‌های پزشکان و پرسنل', PractitionerGroupForm, PractitionerGroup)}
    if kind not in options: return redirect('definitions')
    title, form_class, model = options[kind]
    form = form_class(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        if kind == 'tariffs' and form.cleaned_data.get('apply_to_category'):
            category = form.cleaned_data['category']
            services = MedicalService.objects.filter(category=category, active=True)
            with transaction.atomic():
                for service in services:
                    tariff, _ = InsuranceTariff.objects.get_or_create(service=service, insurance=form.cleaned_data['insurance'], defaults={'patient_share': 0, 'insurer_share': 0})
                    for field, value in form.tariff_values().items():
                        setattr(tariff, field, value)
                    tariff.apply_calculation()
                    tariff.save()
            messages.success(request, f'فرمول برای {services.count()} خدمتِ دستهٔ «{category.name}» ثبت شد.')
        else:
            form.save()
        return redirect('definition_setup', kind=kind)
    items = model.objects.all()
    if kind == 'services': items = items.select_related('category').order_by('category__panel', 'category__name', 'name')
    if kind == 'categories': items = items.order_by('panel', 'name')
    return render(request, 'definitions/setup.html', {
        'title': title,
        'form': form,
        'items': items,
        'kind': kind,
        'is_tariff': kind == 'tariffs',
    })
def index(request):
    form_type = request.POST.get('form_type')
    if request.method == 'POST' and form_type in FORMS:
        form = FORMS[form_type](request.POST)
        if form.is_valid(): form.save(); return redirect('definitions')
    return render(request, 'definitions/index.html', {'category_form': CategoryForm(), 'service_form': ServiceForm(), 'insurance_form': InsuranceForm(), 'tariff_form': TariffForm(), 'categories': ServiceCategory.objects.all().order_by('panel', 'name'), 'services': MedicalService.objects.select_related('category').order_by('category__panel', 'category__name', 'name'), 'insurances': InsuranceProvider.objects.all(), 'tariffs': InsuranceTariff.objects.select_related('service','insurance').order_by('service__category__panel', 'service__category__name', 'service__name')})


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
        headers = ['کد دسته', 'کد داخلی', 'کد استاندارد', 'نام خدمت']
    elif kind == 'services':
        headers = ['کد دسته', 'کد داخلی', 'کد استاندارد', 'نام خدمت']
    else:
        headers = ['کد خدمت', 'سازمان بیمه', 'نام بیمه', 'روش قیمت گذاری', 'مبلغ کل ثابت', 'ضریب K فنی', 'ضریب K حرفه‌ای', 'روش سهم', 'سهم بیمار', 'سهم سازمان', 'سهم تکمیلی', 'مابه التفاوت', 'درصد سهم بیمار', 'درصد سهم سازمان', 'درصد سهم تکمیلی', 'درصد مابه التفاوت']
    def column_name(index):
        name = ''
        while index:
            index, remainder = divmod(index - 1, 26)
            name = chr(65 + remainder) + name
        return name
    cells = ''.join(f'<c r="{column_name(index)}1" t="inlineStr"><is><t>{escape(header)}</t></is></c>' for index, header in enumerate(headers, 1))
    validations = ''
    if kind == 'tariffs':
        validations = '<dataValidations count="2"><dataValidation type="list" allowBlank="1" sqref="D2:D1000"><formula1>"مبلغ ثابت,محاسبه بر اساس K"</formula1></dataValidation><dataValidation type="list" allowBlank="1" sqref="H2:H1000"><formula1>"مبلغ ریالی,درصد از مبلغ کل"</formula1></dataValidation></dataValidations>'
    sheet = f'<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1">{cells}</row></sheetData>{validations}</worksheet>'
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
