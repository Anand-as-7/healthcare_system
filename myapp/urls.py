from django.urls import path
from .import views

urlpatterns = [

    path('',views.index,name='index'),
    path('loginpage',views.loginpage,name='loginpage'),
    path('admin_dashboard',views.admin_dashboard,name='admin_dashboard'),
    path('user_dashboard',views.user_dashboard,name='user_dashboard'),
    path('doctor_dashboard',views.doctor_dashboard,name='doctor_dashboard'),
    path('hospital_dashboard',views.hospital_dashboard,name='hospital_dashboard'),
    path('user_register',views.user_register,name='user_register'),
    path('hospital_register',views.hospital_register,name='hospital_register'),


    
]   
