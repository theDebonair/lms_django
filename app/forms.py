from django import forms
from django.contrib.auth.models import User
from . import models

class IssuedBookForm(forms.Form):
    #to_field_name value will be stored when form is submitted.....__str__ method of book model will be shown there in html
    isbn2=forms.ModelChoiceField(queryset=models.Book.objects.all(),empty_label="Name & ISBN", to_field_name="isbn",label='Name & ISBN')
    roll_no2=forms.ModelChoiceField(queryset=models.Student.objects.all(),empty_label="Name & Enrollment Number",to_field_name='roll_no',label='Name & Enrollment Number')