from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.contrib import messages

# Create your views here.


def patient_dashboard(request):
    return render(request,'patient_dashboard.html')

def doctor_dashboard(request):
    return render(request,'doctor_dashboard.html')

def hospital_dashboard(request):
    return render(request,'hospital_dashboard.html')

def admin_dashboard(request):
    return render(request,'admin_dashboard.html')

def loginpage(request):
    return render(request,'login.html')

def user_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        form2 = LoginForm(request.POST)
        if form.is_valid() and form2.is_valid():
            login=form2.save(commit=False)
            login.usertype='user'
            login.save()
            user = form.save(commit=False)
            user.loginid = login
            user.save()
            messages.success(request, 'User registered successfully')
            return redirect('/')
    else:
        form = UserRegisterForm()
        form2=LoginForm()
    return render(request, 'user_register.html', {'form': form,'form2':form2})
