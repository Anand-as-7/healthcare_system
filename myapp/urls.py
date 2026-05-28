from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('',views.index,name='index'),
    path('loginpage',views.loginpage,name='loginpage'),
    path('admin_dashboard',views.admin_dashboard,name='admin_dashboard'),
    path('user_dashboard',views.user_dashboard,name='user_dashboard'),
    path('doctor_dashboard',views.doctor_dashboard,name='doctor_dashboard'),
    path('hospital_dashboard',views.hospital_dashboard,name='hospital_dashboard'),
    
    path('logout',views.logout_user,name='logout'),
    path('user_register',views.user_register,name='user_register'),
    path('hospital_register',views.hospital_register,name='hospital_register'),
    path('adminusersview',views.adminusersview,name='adminusersview'),
    path('adminhospitalsview',views.adminhospitalsview,name='adminhospitalsview'),
    path('admindoctorsview',views.admindoctorsview,name='admindoctorsview'),
    path('approve_hospital/<int:id>/', views.approve_hospital, name='approve_hospital'),
    path('reject_hospital/<int:id>/', views.reject_hospital, name='reject_hospital'),


    path('doctor_register', views.doctor_register, name='doctor_register'),
    path('hospitaldoctorsview', views.hospitaldoctorsview, name='hospitaldoctorsview'),
    path('userdoctorsview', views.userdoctorsview, name='userdoctorsview'),

    path('bookappointment/<int:id>/', views.bookappointment, name='bookappointment'),
    path('slotadding/<int:id>/', views.slotadding, name='slotadding'),
    path('delete_slot/<int:slot_id>/', views.delete_slot, name='delete_slot'),








    
]   
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
