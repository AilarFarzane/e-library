from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPES = (
        ('admin', 'Admin'),
        ('librarian', 'Librarian'),
        ('member', 'Member'),
    )
    role = models.CharField(max_length=50, choices=USER_TYPES, default='member')
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)



