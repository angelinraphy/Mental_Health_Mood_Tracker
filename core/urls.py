from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    path('patient/', views.patient_dashboard, name='patient_dashboard'),
    path('caregiver/', views.caregiver_dashboard, name='caregiver_dashboard'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('researcher/', views.researcher_dashboard, name='researcher_dashboard'),
    path('user/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
    path('mood/add/', views.MoodCreateView.as_view(), name='mood_add'),
    path('mood/<int:pk>/edit/', views.MoodUpdateView.as_view(), name='mood_edit'),
    path('mood/<int:pk>/delete/', views.MoodDeleteView.as_view(), name='mood_delete'),
    path('prescribe/<int:patient_id>/', views.PrescriptionCreateView.as_view(), name='prescribe_medicine'),


    # Password Change
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='core/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='core/password_change_done.html'), name='password_change_done'),

    # Custom Password Reset via Username and DOB
    path('password_reset/', views.ForgotPasswordVerificationView.as_view(), name='password_reset'),
    path('set_new_password/', views.SetNewPasswordView.as_view(), name='set_new_password'),
]

# Force python cache reload
