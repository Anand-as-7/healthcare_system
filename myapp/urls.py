from django.urls import path
from .import views

urlpatterns = [

    path('loginpage',views.loginpage,name='loginpage'),
    path('admin_dashboard',views.admin_dashboard,name='admin_dashboard'),
    path('user_dashboard',views.user_dashboard,name='user_dashboard'),
    path('doctor_dashboard',views.doctor_dashboard,name='doctor_dashboard'),
    path('hospital_dashboard',views.hospital_dashboard,name='hospital_dashboard'),
    
]
