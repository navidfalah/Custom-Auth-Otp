from django.contrib.auth.backends import ModelBackend
from requests import Response
from .models import User


class MobileBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        if 'phone' in kwargs:
            phone = kwargs['phone']
            try:
                user = User.objects.get(phone=phone, password=password)
            except User.DoesNotExist:
                pass
            