from django import forms
from .models import *

class LoginForm(forms.Form):
    class Meta:
        model=Login
        fields=['email', 'password']

class UserRegisterForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['name', 'address', 'gender', 'age', 'contactnumber','district']