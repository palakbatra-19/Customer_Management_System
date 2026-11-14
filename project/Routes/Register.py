from django.urls import path
from project.Controller import Register
from django.contrib.auth import views as auth_views

app_name = "Register"
urlpatterns = [
    path('signup/', Register.SignupPage, name='Signup'),
    path('login/', Register.LoginPage, name='Login'),
    path('logout/', Register.LogoutPage, name='Logout'),                      #own function register
    path('', Register.LoginPage, name='root'),
    
    path("password-change/", Register.ChangePasswordPage, name="PasswordChange"), 

    # Forgot password
    path("password-reset/",auth_views.PasswordResetView.as_view(template_name="Register/PasswordReset.html",email_template_name="Register/PasswordResetEmail.html",success_url="/register/password-reset/done/" ),name="PasswordReset"),       # django class-based view

    path("password-reset/done/",auth_views.PasswordResetDoneView.as_view(template_name="Register/PasswordResetDone.html"),name="PasswordResetDone"),

    path("password-reset-confirm/<uidb64>/<token>/",auth_views.PasswordResetConfirmView.as_view(template_name="Register/PasswordResetConfirm.html",success_url="/register/password-reset-complete/"),name="PasswordResetConfirm"),

    path("password-reset-complete/",auth_views.PasswordResetCompleteView.as_view(template_name="Register/PasswordResetComplete.html"),name="PasswordResetComplete"),

   
]