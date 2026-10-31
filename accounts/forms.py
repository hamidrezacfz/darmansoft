from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
class UserForm(forms.Form):
    username=forms.CharField(label='نام کاربری')
    password=forms.CharField(label='رمز عبور',widget=forms.PasswordInput,required=False)
    role=forms.ChoiceField(label='سطح دسترسی',choices=UserProfile.Role.choices)
    active_panels=forms.MultipleChoiceField(label='پنل‌های فعال',choices=(),required=False,widget=forms.CheckboxSelectMultiple)
    permissions=forms.MultipleChoiceField(label='دسترسی به بخش‌ها و عملیات',choices=(
        ('reception','پذیرش'),('appointments','نوبت‌دهی'),('definitions','تعاریف پایه'),
        ('billing','صندوق'),('accounting','حسابداری و امور مالی'),('inventory','انبار'),
        ('insurance','بیمه و تعرفه‌ها'),('records','پرونده و سوابق'),('reports','گزارش‌ها'),
        ('users','کاربران و تنظیمات'),('view','مشاهده'),('create','ثبت'),
        ('edit','ویرایش'),('delete','حذف'),('refund','استرداد وجه')
    ),required=False,widget=forms.CheckboxSelectMultiple)
    def __init__(self,*args,profile=None,**kwargs):
        super().__init__(*args,**kwargs)
        self.profile=profile
        from definitions.models import ServiceCategory
        self.fields['active_panels'].choices=ServiceCategory.Panel.choices
        if profile:
            self.initial.update(username=profile.user.username,role=profile.role,active_panels=profile.active_panels,permissions=profile.permissions)
    def clean_username(self):
        value=self.cleaned_data['username']
        qs=User.objects.filter(username=value)
        if getattr(self,'profile',None): qs=qs.exclude(pk=self.profile.user_id)
        if qs.exists(): raise forms.ValidationError('این نام کاربری قبلاً ثبت شده است.')
        return value
