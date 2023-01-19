from django.db import models
from statistics import mode
from django.db import models
from django.contrib.auth.models import AbstractUser
from user_auth.myusermanager import MyUserManager


class User(AbstractUser):
    username = None
    phone = models.CharField(max_length=11, unique=True)
    is_verified = models.BooleanField(default=False)
    verifyCode = models.PositiveIntegerField(blank=True, null=True)
    verifyCode_create_time = models.DateTimeField(auto_now=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified = models.DateTimeField(auto_now=True, blank=True, null=True)
    objects = MyUserManager()
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []
    backend = 'user_auth.mybackend.MobileBackend'
