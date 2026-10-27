from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import User
from .forms import UserForm
from .models import UserProfile
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from .decorators import role_required
from django.shortcuts import render

def login_view(request):
    error = ''
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user:
            login(request, user); return redirect('/')
        error = 'نام کاربری یا رمز عبور نادرست است.'
    return render(request, 'accounts/login.html', {'error': error})

def logout_view(request):
    logout(request); return redirect(settings.LOGIN_URL)

@role_required(UserProfile.Role.ADMIN)
def index(request):
    form=UserForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        user=User.objects.create_user(username=form.cleaned_data['username'],password=form.cleaned_data['password'])
        UserProfile.objects.create(user=user,role=form.cleaned_data['role'])
        return redirect('users')
    return render(request,'accounts/index.html',{'form':form,'users':UserProfile.objects.select_related('user')})

# Create your views here.
