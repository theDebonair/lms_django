from pickle import FALSE
from django.core.mail import send_mail
from lms import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.decorators import login_required
from . tokens import generate_token
from django.db.models import Q
from . models import *
from . forms import *


def index(request):
    return render(request, 'app/index.html')


@login_required(login_url='/signin')
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
                return redirect('profile')
            else:
                messages.error(request, 
                    "This is an Student account. Please Sign-In here.")
                return redirect('signin')
        else:
            alert = True
            messages.error(request, "Invalid Username & Password.")

    return render(request, "app/admin_login.html")


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)

            if request.user.is_superuser:
                messages.error(request, 
                    "This is an ADMIN account. Please Sign-In here.")
                return redirect('admin_login')

            elif request.user.is_active is FALSE:
                messages.error(request, 
                    "Please activate your account via activation link sent to your registered E-Mail ID. Contact ADMIN if any problem persists.")

            else:
                return redirect('profile')

        else:
            alert = True
            messages.error(request, "Invalid Username & Password.")
    return render(request, 'app/signin.html')


def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        roll_no = request.POST['roll_no']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if User.objects.filter(username=username):
            messages.error(
                request, "Username already exist! Please try some other username.")
            return redirect('signuppage')

        if len(username) > 20:
            messages.error(request, "Username must be under 20 characters.")
            return redirect('signuppage')

        if not username.isalnum():
            messages.error(request, "Username must be alpha-numeric.")
            return redirect('signuppage')

        if not username.islower():
            messages.error(request, "Username must be in lowercase.")
            return redirect('signuppage')

        if User.objects.filter(email=email).exists():
            messages.error(request, "E-Mail ID already registered.")
            return redirect('signinpage')

        if password != confirm_password:
            messages.error(request, "Password didn't matched.")
            return redirect('signuppage')

        user = User.objects.create_user(
            username=username, email=email, password=password)
        user.is_active = False
        user.save()
        student = Student.objects.create(user=user, roll_no=roll_no)
        student.save()
        alert = True

        # Confirmation E-mail
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = generate_token.make_token(user)
        current_site = get_current_site(request)
        subject = "Welcome to LMS!"
        message = "Hello " + user.username + "!\n\n" + "Welcome to LMS. Your account has been created successfully. Please click the link below to activate your account.\n\nConfirmation Link: http://" + \
            current_site.domain + "/activate/" + uidb64 + \
            "/" + token + "\n\nRegards\nTeam LMS"
        from_email = settings.EMAIL_HOST_USER
        to_list = [user.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        messages.success(request, 
            "Activation E-Mail sent to your registered E-Mail address.")
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


@login_required(login_url='/admin_login')
def addbook(request):
    if request.method == "POST":
        name = request.POST['name']
        author = request.POST['author']
        isbn = request.POST['isbn']
        category = request.POST['category']
        profile_pic = request.FILES['profile_pic']

        books = Book.objects.create(
            name=name, author=author, isbn=isbn, category=category, profile_pic=profile_pic)
        books.save()
        alert = True
        messages.success(request, "Book is added successfully.")
    return render(request, "app/addbook.html")


@login_required(login_url='/signin')
def viewbook(request):
    search_query = ''

    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')

    books = Book.objects.filter(Q(name__icontains=search_query) | Q(
        author__icontains=search_query) | Q(category__icontains=search_query))

    return render(request, "app/viewbook.html", {'books': books})


def delete_book(request, myid):
    books = Book.objects.filter(id=myid)
    books.delete()
    return redirect('viewbook')


@login_required(login_url="/admin_login")
def view_student(request):
    search_student = ''

    if request.GET.get('search_student'):
        search_student = request.GET.get('search_student')

    students = Student.objects.filter(roll_no__icontains=search_student)

    return render(request, "app/view_student.html", {'students': students})


def delete_student(request, myid):
    students = Student.objects.filter(id=myid)
    students.delete()
    return redirect('view_student')


def editprofile(request):
    return render(request, 'app/editprofile.html')


def issuebook_view(request):
    form = IssuedBookForm()
    if request.method == 'POST':
        # now this form have data from html
        form = IssuedBookForm(request.POST)
        if form.is_valid():
            obj = IssuedBook()
            obj.roll_no = request.POST.get('roll_no2')
            obj.isbn = request.POST.get('isbn2')
            obj.save()
            return render(request, 'app/profile.html')
    return render(request, 'app/issuebook.html', {'form': form})


def viewissuebook_view(request):
    issuedbooks = IssuedBook.objects.all()
    li = []
    for ib in issuedbooks:
        issdate = str(ib.issuedate.day)+'-' + \
            str(ib.issuedate.month)+'-'+str(ib.issuedate.year)
        expdate = str(ib.expirydate.day)+'-' + \
            str(ib.expirydate.month)+'-'+str(ib.expirydate.year)
        # fine calculation
        days = (date.today()-ib.issuedate)
        print(date.today())
        d = days.days
        fine = 0
        if d > 15:
            day = d-15
            fine = day*10
        books = list(Book.objects.filter(isbn=ib.isbn))
        students = list(Student.objects.filter(roll_no=ib.roll_no))
        i = 0
        for l in books:
            t = (students[i].user, students[i].roll_no,
                 books[i].name, books[i].author, issdate, expdate, fine)
            i = i+1
            li.append(t)

    return render(request, 'app/viewissuebook.html', {'li': li})
