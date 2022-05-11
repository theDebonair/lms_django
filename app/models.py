from django.db import models
from django.contrib.auth.models import User
from datetime import datetime,timedelta


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_no = models.CharField(max_length=3, blank=True)

    def __str__(self):
        return str(self.user)

class Book(models.Model):
    name = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.PositiveIntegerField()
    category = models.CharField(max_length=50)
    profile_pic = models.ImageField(null=True, blank=True)

    def __str__(self):
        return str(self.name) + " ["+str(self.isbn)+']'

def get_expiry():
    return datetime.today() + timedelta(days=15)

class IssuedBook(models.Model):
    roll_no=models.CharField(max_length=30, blank=True)
    isbn=models.CharField(max_length=30)
    issuedate = models.DateField(auto_now=True)
    expirydate = models.DateField(default=get_expiry)
    def __str__(self):
        return self.roll_no