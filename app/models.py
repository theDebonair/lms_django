from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_no = models.CharField(max_length=3)

    def __str__(self):
        return str(self.user)
