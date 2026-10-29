"""Robust, all-or-nothing imports for CSV and Excel workbooks."""
import csv
import io
import re
import zipfile
from decimal import Decimal, InvalidOperation
from xml.etree import ElementTree as ET

from django.db import transaction
from .models import InsuranceProvider, InsuranceTariff, MedicalService, ServiceCategory

NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
DOC_REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'

def _cell_col(ref):
    n = 0
    for char in re.match(r'[A-Z]+', ref).group(0):
        n = n * 26 + ord(char) - 64
    return n - 1

def _text(node):
    return ''.join(node.itertext()) if node is not None else ''

def _xlsx_rows(upload):
    """Read the first Excel worksheet, including inline text and blank cells."""
    book = zipfile.ZipFile(upload)
    ns = f'{{{NS}}}'
    shared = []
    if 'xl/sharedStrings.xml' in book.namelist():
        root = ET.fromstring(book.read('xl/sharedStrings.xml'))
        shared = [_text(item) for item in root.findall(f'{ns}si')]
    try:
        workbook = ET.fromstring(book.read('xl/workbook.xml'))
        sheet = workbook.find(f'.//{ns}sheets/{ns}sheet')
        relation_id = sheet.get(f'{{{DOC_REL}}}id')
        rels = ET.fromstring(book.read('xl/_rels/workbook.xml.rels'))
        target = next(r.get('Target') for r in rels.findall(f'{{{REL}}}Relationship') if r.get('Id') == relation_id)
        sheet_path = target if target.startswith('xl/') else 'xl/' + target.lstrip('/')
    except (AttributeError, KeyError, StopIteration):
        sheet_path = 'xl/worksheets/sheet1.xml'
    root = ET.fromstring(book.read(sheet_path))
    result = []
    for row in root.findall(f'.//{ns}sheetData/{ns}row'):
        values = []
        for cell in row.findall(f'{ns}c'):
            index = _cell_col(cell.get('r', 'A1'))
            values.extend([''] * (index + 1 - len(values)))
            kind = cell.get('t')
            if kind == 'inlineStr':
                values[index] = _text(cell.find(f'{ns}is'))
            else:
                raw = _text(cell.find(f'{ns}v'))
                values[index] = shared[int(raw)] if kind == 's' and raw else raw
        result.append(values)
    return result

def read_rows(upload):
    upload.seek(0)
    if upload.name.lower().endswith('.csv'):
        return list(csv.reader(io.StringIO(upload.read().decode('utf-8-sig'))))
    if upload.name.lower().endswith('.xlsx'):
        return _xlsx_rows(upload)
    raise ValueError('فقط فایل Excel با پسوند xlsx یا CSV قابل ورود است.')

def _normal(value):
    return str(value).replace('﻿', '').replace('‌', ' ').replace('ي', 'ی').replace('ك', 'ک').strip().lower()

def _headers(row):
    values = {}
    for index, value in enumerate(row):
        name = _normal(value)
        if name:
            if name in values:
                raise ValueError(f'عنوان ستون «{value}» تکراری است.')
            values[name] = index
    return values

def _value(row, headers, *names):
    for name in names:
        index = headers.get(_normal(name))
        if index is not None and index < len(row):
            return str(row[index]).strip()
    return ''

def _amount(value, title, positive=False):
    value = str(value).replace(',', '').replace('،', '').replace('٬', '').strip()
    if not value:
        raise ValueError(f'«{title}» خالی است.')
    try:
        amount = Decimal(value)
    except InvalidOperation:
        raise ValueError(f'«{title}» باید عدد باشد.')
    if amount < 0 or (positive and not amount):
        raise ValueError(f'«{title}» نامعتبر است.')
    return amount

def _required(headers, *names):
    if any(_normal(name) not in headers for name in names):
        raise ValueError('ستون‌های لازم: ' + '، '.join(names))

def _find_service(code, standard_code, category, name):
    if code:
        return MedicalService.objects.filter(code=code).first()
    if standard_code:
        return MedicalService.objects.filter(standard_code=standard_code).first()
    return MedicalService.objects.filter(category__name=category, name=name).first()

def _parse_services(upload, imaging=False):
    rows = read_rows(upload)
    if not rows:
        raise ValueError('فایل خالی است.')
    headers = _headers(rows[0])
    primary = 'گروه خدمت' if imaging else 'دسته'
    _required(headers, primary, 'نام خدمت', 'تعرفه آزاد')
    allowed = {'تصویربرداری', 'سی تی اسکن', 'سونوگرافی', 'MRI'}
    records, errors, seen = [], [], set()
    for number, row in enumerate(rows[1:], 2):
        if not any(str(v).strip() for v in row):
            continue
        try:
            category = _value(row, headers, primary, 'دسته', 'گروه')
            name = _value(row, headers, 'نام خدمت', 'نام')
            code = _value(row, headers, 'کد داخلی', 'کد')
            standard = _value(row, headers, 'کد استاندارد')
            price = _amount(_value(row, headers, 'تعرفه آزاد', 'تعرفه'), 'تعرفه آزاد', True)
            if not category or not name:
                raise ValueError('دسته و نام خدمت الزامی است.')
            if imaging and category not in allowed:
                raise ValueError('گروه خدمت نامعتبر است.')
            key = code or standard or f'{category}|{name}'
            if key in seen:
                raise ValueError('این خدمت در فایل تکراری است.')
            seen.add(key)
            records.append((category, name, code, standard, price))
        except ValueError as exc:
            errors.append(f'ردیف {number}: {exc}')
    return records, errors

def _save_services(records):
    created = updated = 0
    with transaction.atomic():
        for category_name, name, code, standard, price in records:
            category, _ = ServiceCategory.objects.get_or_create(name=category_name)
            service = _find_service(code, standard, category_name, name)
            values = {'category': category, 'name': name, 'base_price': price, 'active': True}
            if code: values['code'] = code
            if standard: values['standard_code'] = standard
            if service:
                for field, value in values.items(): setattr(service, field, value)
                service.save(); updated += 1
            else:
                MedicalService.objects.create(**values); created += 1
    return created, updated

def import_services(upload):
    records, errors = _parse_services(upload)
    return (*_save_services(records), []) if not errors else (0, 0, errors)

def import_imaging_services(upload):
    records, errors = _parse_services(upload, True)
    return (*_save_services(records), []) if not errors else (0, 0, errors)

def import_tariffs(upload):
    rows = read_rows(upload)
    if not rows: raise ValueError('فایل خالی است.')
    headers = _headers(rows[0])
    _required(headers, 'کد خدمت', 'سازمان بیمه', 'نام بیمه', 'سهم بیمار', 'سهم بیمه')
    records, errors, seen = [], [], set()
    for number, row in enumerate(rows[1:], 2):
        if not any(str(v).strip() for v in row): continue
        try:
            code = _value(row, headers, 'کد خدمت', 'کد استاندارد خدمت')
            service = MedicalService.objects.filter(code=code).first() or MedicalService.objects.filter(standard_code=code).first()
            organization, name = _value(row, headers, 'سازمان بیمه'), _value(row, headers, 'نام بیمه')
            if not (code and service and organization and name): raise ValueError('کد خدمت معتبر، سازمان و نام بیمه الزامی است.')
            key = (service.pk, _normal(organization), _normal(name))
            if key in seen: raise ValueError('این تعرفه در فایل تکراری است.')
            seen.add(key)
            records.append((service, organization, name, _amount(_value(row, headers, 'سهم بیمار'), 'سهم بیمار'), _amount(_value(row, headers, 'سهم بیمه'), 'سهم بیمه'), _amount(_value(row, headers, 'سهم بیمه تکمیلی') or '0', 'سهم تکمیلی')))
        except ValueError as exc: errors.append(f'ردیف {number}: {exc}')
    if errors: return 0, 0, errors
    created = updated = 0
    with transaction.atomic():
        for service, organization, name, patient, insurer, supplementary in records:
            insurance, _ = InsuranceProvider.objects.get_or_create(organization=organization, name=name)
            _, made = InsuranceTariff.objects.update_or_create(service=service, insurance=insurance, defaults={'patient_share': patient, 'insurer_share': insurer, 'supplementary_share': supplementary})
            created += made; updated += not made
    return created, updated, []
