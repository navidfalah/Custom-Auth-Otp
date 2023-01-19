from rest_framework import serializers
from .models import User
from user_auth import helper
from django.utils import timezone

class GateSerializer(serializers.Serializer):
    cash = serializers.IntegerField()
    
class VerifySerializer(serializers.Serializer):
    verifyCode = serializers.IntegerField()
    phone = serializers.CharField(max_length=11)

class PhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11)

class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=20)

class RegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11)
    password = serializers.CharField(max_length=20)
    
    def create(self, validated_data):
        created_password = secrets.token_urlsafe(9)
        otp = helper.otp_generator()
        print(otp)
        phone_number = validated_data['phone']
        helper.send_otp(phone_number, otp)
        user = User.objects.create(phone=phone_number,password = created_password,otp=otp,otp_create_time=timezone.now)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone', 'id']
