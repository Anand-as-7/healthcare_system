from django import forms
from .models import *

class LoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Login
        fields = ['email', 'password']

class UserRegisterForm(forms.ModelForm):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    gender = forms.ChoiceField(choices=GENDER_CHOICES,widget=forms.RadioSelect(attrs={'class': 'form-check-input'}))   
    class Meta:
        model = User
        fields = ['name', 'address', 'gender', 'age','district', 'contactnumber']   

class HospitalRegisterForm(forms.ModelForm):
   
    class Meta:
        model = Hospital
        fields = ['hospital_name', 'address', 'district', 'city','contact']   

class DoctorRegisterForm(forms.ModelForm):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    gender = forms.ChoiceField(choices=GENDER_CHOICES,widget=forms.RadioSelect(attrs={'class': 'form-check-input'})) 
   
    class Meta:
        model = Doctor
        fields = ['doctor_name', 'photo', 'gender', 'dob','specialization','experience','contact']   