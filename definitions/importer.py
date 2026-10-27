"""Small dependency-free importer for Excel (.xlsx) and CSV files."""
import csv
import io
import zipfile
from decimal import Decimal, InvalidOperation
from xml.etree import ElementTree as ET

from .models import InsuranceProvider, InsuranceTariff, MedicalService, ServiceCategory


def _xlsx_rows(upload):
    book = zipfile.ZipFile(upload)
    ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
    shared = []
    if 'xl/sharedStrings.xml' in book.namelist():
        root = ET.fromstring(book.read('xl/sharedStrings.xml'))
        shared = [''.join(node.itertext()) for node in root.findall(f'{ns}si')]
    root = ET.fromstring(book.read('xl/worksheets/sheet1.xml'))
    rows = []
    for row in root.findall(f'.//{ns}row'):
        values = []
        for cell in row.findall(f'{ns}c'):
            value = cell.find(f'{ns}v')
            raw = '' if value is None else value.text or ''
            values.append(shared[int(raw)] if cell.get('t') == 's' and raw else raw)
        rows.append(values)
    return rows


def read_rows(upload):
    if upload.name.lower().endswith('.csv'):
        text = upload.read().decode('utf-8-sig')
        return list(csv.reader(io.StringIO(text)))
    if upload.name.lower().endswith('.xlsx'):
        return _xlsx_rows(upload)
    raise ValueError('فقط فایل Excel با پسوند xlsx یا CSV قابل ورود است.')


def _value(row, headers, *names):
    for name in names:
        if name in headers and headers[name] < len(row): return str(row[headers[name]]).strip()
    return ''


def _amount(value):
    return Decimal(str(value).replace(',', '').replace('،', '').strip() or '0')


def import_services(upload):
    rows = read_rows(upload)
    if not rows: raise ValueError('فایل خالی است.')
    headers = {str(value).strip().lower(): index for index, value in enumerate(rows[0])}
    required = ('دسته', 'نام خدمت', 'تعرفه آزاد')
    if not all(name in headers for name in required): raise ValueError('ستون‌های لازم: دسته، نام خدمت، تعرفه آزاد')
    created = updated = 0; errors = []
    for number, row in enumerate(rows[1:], start=2):
        if not any(str(x).strip() for x in row): continue
        try:
            category_name = _value(row, headers, 'دسته', 'دسته‌بندی', 'category')
            name = _value(row, headers, 'نام خدمت', 'نام', 'name')
            code = _value(row, headers, 'کد داخلی', 'کد', 'code')
            standard_code = _value(row, headers, 'کد استاندارد', 'standard_code')
            price = _amount(_value(row, headers, 'تعرفه آزاد', 'تعرفه', 'base_price'))
            if not category_name or not name: raise ValueError('دسته و نام خدمت الزامی است.')
            category, _ = ServiceCategory.objects.get_or_create(name=category_name)
            defaults = {'category': category, 'standard_code': standard_code or None, 'name': name, 'base_price': price, 'active': True}
            if code:
                _, made = MedicalService.objects.update_or_create(code=code, defaults=defaults)
                created += made; updated += not made
            else:
                MedicalService.objects.create(code=None, **defaults); created += 1
        except (ValueError, InvalidOperation, Exception) as exc:
            errors.append(f'ردیف {number}: {exc}')
    return created, updated, errors


def import_tariffs(upload):
    rows = read_rows(upload)
    if not rows: raise ValueError('فایل خالی است.')
    headers = {str(value).strip().lower(): index for index, value in enumerate(rows[0])}
    required = ('کد خدمت', 'سازمان بیمه', 'نام بیمه', 'سهم بیمار', 'سهم بیمه')
    if not all(name in headers for name in required): raise ValueError('ستون‌های لازم: کد خدمت، سازمان بیمه، نام بیمه، سهم بیمار، سهم بیمه')
    created = updated = 0; errors = []
    for number, row in enumerate(rows[1:], start=2):
        if not any(str(x).strip() for x in row): continue
        try:
            code = _value(row, headers, 'کد خدمت', 'service_code')
            service = MedicalService.objects.get(code=code)
            organization = _value(row, headers, 'سازمان بیمه', 'organization')
            name = _value(row, headers, 'نام بیمه', 'insurance_name')
            insurance, _ = InsuranceProvider.objects.get_or_create(organization=organization, name=name)
            defaults = {'patient_share': _amount(_value(row, headers, 'سهم بیمار', 'patient_share')), 'insurer_share': _amount(_value(row, headers, 'سهم بیمه', 'insurer_share')), 'supplementary_share': _amount(_value(row, headers, 'سهم بیمه تکمیلی', 'supplementary_share'))}
            _, made = InsuranceTariff.objects.update_or_create(service=service, insurance=insurance, defaults=defaults)
            created += made; updated += not made
        except (ValueError, MedicalService.DoesNotExist, Exception) as exc:
            errors.append(f'ردیف {number}: {exc}')
    return created, updated, errors
