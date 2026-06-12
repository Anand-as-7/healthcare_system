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

    path('payment/<int:id>/', views.payment, name='payment'),
    path('bookingconfirmation/<int:id>/', views.bookingconfirmation, name='bookingconfirmation'),
    path('bookingconfirmation/<int:id>/receipt/', views.download_receipt, name='download_receipt'),


    path('user_appointmentsview', views.user_appointmentsview, name='user_appointmentsview'),
    path('user_appointmentdetailsview/<int:id>/', views.user_appointmentdetailsview, name='user_appointmentdetailsview'),

    path('resheduleappointment/<int:id>/', views.resheduleappointment, name='resheduleappointment'),
    path('cancelappointment/<int:id>/', views.cancelappointment, name='cancelappointment'),

    path('doctorappointmentsview', views.doctorappointmentsview, name='doctorappointmentsview'),

    path('videoconference/<int:id>/', views.videoconference, name='videoconference'),
    path('save-appointment-url/<int:id>/', views.save_appointment_url, name='save_appointment_url'),

    path('user_complaints', views.user_complaints, name='user_complaints'),



    # ── AI Chatbot + X-ray Prediction ─────────────────────────
    path('ai-chatbot/', views.ai_chatbot_predict, name='ai_chatbot'),
 
    # ── AI Diet & Health Suggestions ──────────────────────────
    path('ai-diet/', views.ai_diet_suggestions, name='ai_diet'),
 
    # ── Medical History ────────────────────────────────────────
    path('medical-history/', views.user_medical_history, name='user_medical_history'),







    
]   
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
