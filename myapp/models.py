from django.db import models

# Create your models here.


class Login(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    usertype = models.CharField(max_length=20)
    status = models.IntegerField(default=0)

class User(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    gender = models.CharField(max_length=20)
    age = models.IntegerField()
    contactnumber = models.CharField(max_length=12)
    district = models.CharField(max_length=50)
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE)

