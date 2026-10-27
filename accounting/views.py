from decimal import Decimal
from django.db.models import Sum
from django.shortcuts import redirect, render
from billing.models import Payment
from reception.models import Admission
from definitions.models import Practitioner
from .forms import FinancialEntryForm, InventoryGroupForm, InventoryItemForm, InventoryMovementForm, InventoryUnitForm, PurchaseInvoiceForm
from .models import FinancialEntry, InventoryGroup, InventoryItem, InventoryMovement, InventoryUnit, PurchaseInvoice
from core.jalali import from_jalali


def dashboard(request):
    forms = {
        'entry': FinancialEntryForm(request.POST or None, prefix='entry'),
        'invoice': PurchaseInvoiceForm(request.POST or None, prefix='invoice'),
    }
    form_name = request.POST.get('form_name')
    if request.method == 'POST' and form_name == 'entry' and forms['entry'].is_valid():
        forms['entry'].save()
        return redirect('accounting_dashboard')
    if request.method == 'POST' and form_name == 'invoice' and forms['invoice'].is_valid():
        invoice = forms['invoice'].save()
        FinancialEntry.objects.create(
            entry_type=FinancialEntry.Type.EXPENSE,
            title=f'فاکتور خرید: {invoice.supplier}',
            category='خرید و تأمین کالا',
            document_number=invoice.invoice_number,
            amount=invoice.total_amount,
            entry_date=invoice.invoice_date,
            note=f'ثبت خودکار از فاکتور {invoice.invoice_number or "بدون شماره"}',
        )
        return redirect('accounting_dashboard')
    manual_income = FinancialEntry.objects.filter(entry_type=FinancialEntry.Type.INCOME).aggregate(v=Sum('amount'))['v'] or 0
    manual_expense = FinancialEntry.objects.filter(entry_type=FinancialEntry.Type.EXPENSE).aggregate(v=Sum('amount'))['v'] or 0
    patient_income = Payment.objects.aggregate(v=Sum('amount'))['v'] or 0
    return render(request, 'accounting/dashboard.html', {
        'entry_form': forms['entry'], 'invoice_form': forms['invoice'],
        'entries': FinancialEntry.objects.all()[:15], 'invoices': PurchaseInvoice.objects.all()[:10],
        'patient_income': patient_income, 'manual_income': manual_income, 'manual_expense': manual_expense,
        'balance': patient_income + manual_income - manual_expense,
    })


def financial_report(request):
    """Printable filtered view of manually entered accounting documents."""
    entries = FinancialEntry.objects.all()
    entry_type = request.GET.get('entry_type', '')
    category = request.GET.get('category', '').strip()
    query = request.GET.get('q', '').strip()
    date_from, date_to = request.GET.get('date_from', ''), request.GET.get('date_to', '')
    if entry_type in (FinancialEntry.Type.INCOME, FinancialEntry.Type.EXPENSE):
        entries = entries.filter(entry_type=entry_type)
    if category:
        entries = entries.filter(category__icontains=category)
    if query:
        from django.db.models import Q
        entries = entries.filter(Q(title__icontains=query) | Q(document_number__icontains=query) | Q(note__icontains=query))
    for value, lookup in ((date_from, 'entry_date__gte'), (date_to, 'entry_date__lte')):
        try:
            if value:
                entries = entries.filter(**{lookup: from_jalali(value)})
        except (TypeError, ValueError):
            pass
    income = entries.filter(entry_type=FinancialEntry.Type.INCOME).aggregate(v=Sum('amount'))['v'] or 0
    expense = entries.filter(entry_type=FinancialEntry.Type.EXPENSE).aggregate(v=Sum('amount'))['v'] or 0
    categories = FinancialEntry.objects.exclude(category='').values_list('category', flat=True).distinct().order_by('category')
    return render(request, 'accounting/financial_report.html', {
        'entries': entries, 'selected': request.GET, 'categories': categories,
        'income': income, 'expense': expense, 'balance': income - expense, 'count': entries.count(),
    })


def inventory(request):
    item_form = InventoryItemForm(request.POST or None, prefix='item')
    movement_form = InventoryMovementForm(request.POST or None, prefix='movement')
    group_form = InventoryGroupForm(request.POST or None, prefix='group')
    unit_form = InventoryUnitForm(request.POST or None, prefix='unit')
    form_name = request.POST.get('form_name')
    if request.method == 'POST' and form_name == 'group' and group_form.is_valid():
        group_form.save(); return redirect('inventory')
    if request.method == 'POST' and form_name == 'unit' and unit_form.is_valid():
        unit_form.save(); return redirect('inventory')
    if request.method == 'POST' and form_name == 'item' and item_form.is_valid():
        item = item_form.save(commit=False)
        if item.unit_definition:
            item.unit = item.unit_definition.name
        item.save(); return redirect('inventory')
    if request.method == 'POST' and form_name == 'movement' and movement_form.is_valid():
        movement = movement_form.save()
        item = movement.item
        if movement.movement_type == InventoryMovement.Type.IN: item.quantity += movement.quantity
        elif movement.movement_type == InventoryMovement.Type.OUT: item.quantity -= movement.quantity
        else: item.quantity = movement.quantity
        item.save(update_fields=['quantity'])
        return redirect('inventory')
    return render(request, 'accounting/inventory.html', {
        'item_form': item_form, 'movement_form': movement_form, 'group_form': group_form, 'unit_form': unit_form,
        'items': InventoryItem.objects.select_related('group', 'unit_definition'),
        'movements': InventoryMovement.objects.select_related('item')[:20],
    })


def inventory_report(request):
    movements = InventoryMovement.objects.select_related('item', 'item__group')
    group_id, item_id = request.GET.get('group', ''), request.GET.get('item', '')
    movement_type, department = request.GET.get('movement_type', ''), request.GET.get('department', '')
    date_from, date_to = request.GET.get('date_from', ''), request.GET.get('date_to', '')
    if group_id: movements = movements.filter(item__group_id=group_id)
    if item_id: movements = movements.filter(item_id=item_id)
    if movement_type: movements = movements.filter(movement_type=movement_type)
    if department: movements = movements.filter(destination_department__icontains=department)
    for value, lookup in ((date_from, 'movement_date__gte'), (date_to, 'movement_date__lte')):
        try:
            if value: movements = movements.filter(**{lookup: from_jalali(value)})
        except (TypeError, ValueError):
            pass
    incoming = movements.filter(movement_type=InventoryMovement.Type.IN).aggregate(v=Sum('quantity'))['v'] or 0
    outgoing = movements.filter(movement_type=InventoryMovement.Type.OUT).aggregate(v=Sum('quantity'))['v'] or 0
    return render(request, 'accounting/inventory_report.html', {
        'movements': movements, 'groups': InventoryGroup.objects.filter(active=True), 'items': InventoryItem.objects.filter(active=True),
        'types': InventoryMovement.Type.choices, 'selected': request.GET, 'incoming': incoming, 'outgoing': outgoing,
        'count': movements.count(),
    })


def practitioner_shares(request):
    rows = []
    for person in Practitioner.objects.filter(active=True).select_related('group'):
        performance = Admission.objects.filter(practitioner=person).aggregate(v=Sum('patient_share') + Sum('insurer_share') + Sum('supplementary_share'))['v'] or Decimal('0')
        share = performance * person.share_percent / Decimal('100')
        rows.append({'person': person, 'performance': performance, 'share': share})
    return render(request, 'accounting/practitioner_shares.html', {'rows': rows})
