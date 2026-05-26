from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password



# Create your views here.


def index(request):
    return render(request,'index.html')

def user_dashboard(request):
    return render(request,'user_dashboard.html')

def doctor_dashboard(request):
    return render(request,'doctor_dashboard.html')

def hospital_dashboard(request):
    return render(request,'hospital_dashboard.html')

def admin_dashboard(request):
    return render(request,'admin_dashboard.html')



from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import Login


def loginpage(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            login = Login.objects.get(email=email)

        except Login.DoesNotExist:
            messages.error(request, 'User does not exist. Please register first.')
            return redirect('loginpage')

        if not check_password(password, login.password):
            messages.error(request, 'Incorrect email or password.')
            return redirect('loginpage')

        # Normal user can login without status checking
        if login.usertype == 'user':
            request.session['login_id'] = login.id
            request.session['usertype'] = login.usertype
            return redirect('user_dashboard')

        # Hospital approval status
        elif login.usertype == 'hospital':
            if login.status == 0:
                messages.warning(request, 'Your hospital account is waiting for admin approval.')
                return redirect('loginpage')

            elif login.status == 2:
                messages.error(request, 'Your hospital registration has been rejected by the admin.')
                return redirect('loginpage')

            elif login.status == 1:
                request.session['login_id'] = login.id
                request.session['usertype'] = login.usertype
                return redirect('hospital_dashboard')

        # Doctor approval status
        elif login.usertype == 'doctor':
            if login.status == 0:
                messages.warning(request, 'Your doctor account is waiting for hospital approval.')
                return redirect('loginpage')

            elif login.status == 2:
                messages.error(request, 'Your doctor registration has been rejected by the hospital.')
                return redirect('loginpage')

            elif login.status == 1:
                request.session['login_id'] = login.id
                request.session['usertype'] = login.usertype
                return redirect('doctor_dashboard')

        # Admin approval status
        elif login.usertype == 'admin':
            if login.status == 0:
                messages.warning(request, 'Your admin account is not active yet.')
                return redirect('loginpage')

            elif login.status == 1:
                request.session['login_id'] = login.id
                request.session['usertype'] = login.usertype
                return redirect('admin_dashboard')

        messages.error(request, 'Invalid user type or inactive account.')
        return redirect('loginpage')

    return render(request, 'login.html')




def user_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        form2 = LoginForm(request.POST)

        if form.is_valid() and form2.is_valid():
            login = form2.save(commit=False)
            login.usertype = 'user'
            login.password = make_password(form2.cleaned_data['password'])
            login.save()
            user = form.save(commit=False)
            user.loginid = login
            user.save()

            messages.success(request, 'User registered successfully')
            return redirect('index')
    else:
        form = UserRegisterForm()
        form2 = LoginForm()

    return render(request, 'user_register.html', {'form': form,'form2': form2})


def hospital_register(request):
    if request.method == 'POST':
        form = HospitalRegisterForm(request.POST)
        form2 = LoginForm(request.POST)

        if form.is_valid() and form2.is_valid():
            login = form2.save(commit=False)
            login.usertype = 'hospital'
            login.password = make_password(form2.cleaned_data['password'])
            login.save()
            user = form.save(commit=False)
            user.loginid = login
            user.save()

            messages.success(request, 'Hospital registered successfully')
            return redirect('index')
    else:
        form = HospitalRegisterForm()
        form2 = LoginForm()

    return render(request, 'hospital_register.html', {'form': form,'form2': form2})

