from django import forms
from .models import FinancialEntry, PurchaseInvoice, InventoryGroup, InventoryItem, InventoryMovement, InventoryUnit


class JalaliDateField(forms.DateField):
    def prepare_value(self, value):
        if value:
            from core.jalali import to_jalali
            return to_jalali(value)
        return value

    def to_python(self, value):
        if not value:
            return None
        from core.jalali import from_jalali
        try:
            return from_jalali(value)
        except (TypeError, ValueError):
            raise forms.ValidationError('تاریخ را به شکل ۱۴۰۵/۰۷/۲۵ وارد کنید.')


class FinancialEntryForm(forms.ModelForm):
    entry_date = JalaliDateField(label='تاریخ سند', widget=forms.TextInput(attrs={'placeholder': '۱۴۰۵/۰۷/۲۵'}))
    class Meta:
        model = FinancialEntry
        fields = ['entry_type', 'category', 'title', 'document_number', 'amount', 'entry_date', 'note']
        widgets = {
            'category': forms.TextInput(attrs={'list': 'financial-categories', 'placeholder': 'مثلاً اجاره، خرید کالا، سایر'}),
            'document_number': forms.TextInput(attrs={'placeholder': 'مثلاً ۱۴۰۵-۰۰۱'}),
        }


class PurchaseInvoiceForm(forms.ModelForm):
    invoice_date = JalaliDateField(label='تاریخ فاکتور', widget=forms.TextInput(attrs={'placeholder': '۱۴۰۵/۰۷/۲۵'}))
    class Meta:
        model = PurchaseInvoice
        fields = ['supplier', 'invoice_number', 'invoice_date', 'total_amount', 'note']


class InventoryGroupForm(forms.ModelForm):
    class Meta:
        model = InventoryGroup
        fields = ['name', 'active']


class InventoryUnitForm(forms.ModelForm):
    class Meta:
        model = InventoryUnit
        fields = ['name', 'active']


class InventoryItemForm(forms.ModelForm):
    expiration_date = JalaliDateField(label='تاریخ انقضا', required=False, widget=forms.TextInput(attrs={'placeholder': '۱۴۰۵/۰۷/۲۵'}))
    class Meta:
        model = InventoryItem
        fields = ['name', 'group', 'unit_definition', 'quantity', 'reorder_point', 'expiration_date', 'supplier', 'ordered_by', 'requesting_department', 'active']


class InventoryMovementForm(forms.ModelForm):
    movement_date = JalaliDateField(label='تاریخ سند', widget=forms.TextInput(attrs={'placeholder': '۱۴۰۵/۰۷/۲۵'}))
    class Meta:
        model = InventoryMovement
        fields = ['item', 'movement_type', 'quantity', 'unit_price', 'movement_date', 'destination_department', 'document_number', 'note']
