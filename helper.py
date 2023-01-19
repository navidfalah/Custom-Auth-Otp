from random import randint
from .models import User
from django.utils.timezone import timedelta
from django.utils import timezone
from .sms import Api

username = '09117178082'
password = '961SM'

def send_verifyCode(phone, verifyCode): 
    api = Api(username, password)
    sms_rest = api.sms()
    text = [verifyCode, ]
    to = phone
    bodyId = 93017
    sms_rest.send_by_base_number(text, to, bodyId)


def verifyCode_generator():
    return randint(1000, 9999)


def check_verifyCode_expiration(phone):
    try:
        user = User.objects.get(phone=phone)
        now = timezone.now()
        verifyCode_time = user.verifyCode_create_time
        verifyCode_after = verifyCode_time + timedelta(seconds=180)
        if now > verifyCode_after:
            return False
        return True

    except User.DoesNotExist:
        return False
