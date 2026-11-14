from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from project.Models.Customer import Customer
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages



@login_required(login_url='Register:Login')
def SignupPage(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if not username or not email or not password1 or not password2:
            return render(request, "Register/SignupPage.html", {"error": "All fields are required"})

        if password1 != password2:
            return render(request, "Register/SignupPage.html", {"error": "Passwords do not match"})

        if User.objects.filter(username=username).exists():
            return render(request, "Register/SignupPage.html", {"error": "Username already exists"})

        new_user=User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        Customer.objects.create(          
            user=new_user,
            name=username,
            email=email,
            status='lead'
        )

        return redirect("Register:Login")

    return render(request, "Register/SignupPage.html")




def LoginPage(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("Admin:Dashboard")
        return redirect("Customer:Profile")  

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect("Admin:Dashboard")
            return redirect("Customer:Profile")

        return render(request, "Register/LoginPage.html", {"error": "Invalid username or password"})

    return render(request, "Register/LoginPage.html")




@login_required(login_url='Register:Login')
def ChangePasswordPage(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # keeps user logged in after password change
            messages.success(request, "Password updated successfully")
            if request.user.is_staff:
                return redirect("Admin:Dashboard")
            return redirect("Customer:Profile")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "Register/ChangePasswordPage.html", {"form": form})


@login_required(login_url='Register:Login')
def LogoutPage(request):
    logout(request)
    return redirect("Register:Login")

