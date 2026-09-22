from django.urls import path 
from . import views
from django.contrib.auth import views as auth_views
urlpatterns= [
    path('', views.register, name='register'),
    path('email_verification/<str:uidb64>/<str:token>', views.email_verification, name= "email_verification"),
    path('email_verification_sent', views.email_verification_sent, name="email_verification_sent"),
    path('email_verification_success', views.email_verification_success, name="email_verification_success"),
    path('emailverification_failed', views.emailverification_failed, name="emailverification_failed"),
    path('login', views.Login_view, name='login'),
    path('logout', views.logout_view, name="logout"),
    path('dashboard', views.dashboard_view, name='dashboard'),
    path('profile_managment', views.profile_managment, name="profile_managment"),
    path('delete_account', views.delete_account, name="delete_account"),


    path('reset_password', auth_views.PasswordResetView.as_view(template_name='account/password/password_reset.html'), name= "reset_password"),

    path('password_reset_done', auth_views.PasswordResetDoneView.as_view(template_name='account/password/password_reset_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='account/password/password_reset_form.html'), name='password_reset_confirm'),

    path('password_reset_complete', auth_views.PasswordResetCompleteView.as_view(template_name='account/password/password_reset_complete.html'), name='password_reset_complete'),

    path('manage_shipping', views.manage_shipping, name= 'manage_shipping'),

]