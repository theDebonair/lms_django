from base64 import urlsafe_b64decode
from pickle import FALSE
from django.core.mail import EmailMessage, send_mail
from lms import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token
from . models import *
from . forms import *

def index(request):
    return render(request, 'app/index.html')

def profile(request):
    return render(request, 'app/profile.html')

def admin_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            if request.user.is_superuser:
                return redirect("/profile")
            else:
                return HttpResponse("You are not an admin.")
        else:
            alert = True
            return render(request, "app/admin_login.html", {'alert': alert})
    return render(request, "app/admin_login.html")

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)

            if request.user.is_superuser:
                return HttpResponse("this is an admin id go to <a href='admin_login'>Admin Login</a> or <a href= 'home'>home</a>")

            elif request.user.is_active is FALSE:
                return HttpResponse("Please activate your account! <a href='home'>Home</a>")
            
            else:
                return redirect("/profile")

        else:
            alert = True
            return render(request, "app/signin.html", {'alert': alert})
    return render(request, 'app/signin.html')

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        roll_no = request.POST['roll_no']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect('signuppage')

        if len(username)>20:
            messages.error(request, "Username must be under 20 charcters!!")
            return redirect('signuppage')

        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!!")
            return redirect('signuppage')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('signinpage')

        if password != confirm_password:
            messages.error(request, "Password didn't matched!")
            return redirect('signuppage')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False
        user.save()
        student = Student.objects.create(user=user, roll_no=roll_no)
        student.save()
        alert = True

        #Confirmation E-mail
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = generate_token.make_token(user)
        current_site = get_current_site(request)
        subject = "Welcome to LMS!"
        message = "Hello " + user.username + "!\n\n" + "Welcome to LMS. Your account has been created successfully. Please click the link below to activate your account.\n\nConfirmation Link: http://" + current_site.domain + "/activate/" + uidb64 + "/" + token + "\n\nRegards\nTeam LMS"
        from_email = settings.EMAIL_HOST_USER
        to_list = [user.email]
        send_mail(subject , message, from_email, to_list, fail_silently=True)

        return render(request, "app/signup.html", {'alert': alert})
    return render(request, "app/signup.html")

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and generate_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "Your account has been activated!")
        return redirect('signinpage')
    else:
        return render(request, 'activation_failed.html')

def logoutUser(request):
    logout(request)
    return redirect('home')

def forgetpass(request):
    return render(request, 'app/forgetpass.html')
