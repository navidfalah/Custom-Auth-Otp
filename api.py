from sre_parse import State
from rest_framework import generics, status
from rest_framework.response import Response
from .serializer import(
    RegisterSerializer,
    UserSerializer,
    VerifySerializer,
    GateSerializer,
    PhoneSerializer,
    ResetPasswordSerializer
)
from .models import User
from django.contrib.auth import login
from user_auth import helper
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from azbankgateways import bankfactories, models as bank_models, default_settings as settings
from azbankgateways.exceptions import AZBankGatewaysException
from django.http import HttpResponse, Http404
from django.urls import reverse
from azbankgateways import bankfactories, models as bank_models, default_settings as settings
import logging
from rest_framework.views import APIView
from django.contrib import auth 


class CallbackGatewayShop(APIView):

    def get(self, request, *args,  **kwargs):
        tracking_code = request.GET.get(settings.TRACKING_CODE_QUERY_PARAM, None)
        if not tracking_code:
            logging.debug("این لینک معتبر نیست.")
            raise Http404
        try:
            bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
        except bank_models.Bank.DoesNotExist:
            logging.debug("این لینک معتبر نیست.")
            raise Http404
        if bank_record.is_success:
            # payment is successful
            if request.user.is_authenticated:
                request.user.cash += request.user.cash
            return HttpResponse("موفق")
            # product_registered_customer(request.user.mobile, 'hamgramco.ir/bought/')
            # return redirect('bought')
        # payment failed
        return HttpResponse("پرداخت با شکست مواجه شده است. اگر پول کم شده است ظرف مدت ۴۸ ساعت پول به حساب شما بازخواهد گشت.")

class GoToGatewayShop(generics.GenericAPIView):
    serializer_class = GateSerializer

    def post(self, request, *args,  **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.data["cash"]*10
        factory = bankfactories.BankFactory()
        try:
            bank = factory.auto_create() # or factory.create(bank_models.BankType.BMI) or set identifier
            bank.set_request(request)
            bank.set_amount(amount)
            # return url to app
            bank.set_client_callback_url(reverse('user_auth:callback'))
            # bank.set_mobile_number(user_mobile_number)  
            # optional 
            bank_record = bank.ready()
            # going to gateway
            return bank.redirect_gateway()
        except AZBankGatewaysException as e:
            logging.critical(e)
            # TODO: redirect to failed page.
            raise e


class UserRUD(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class VerifyApi(generics.GenericAPIView):
    serializer_class = VerifySerializer

    def post(self, request, *args,  **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        verifyCode = serializer.data['verifyCode']
        phone = serializer.data['phone']
        try:
            user = User.objects.get(phone=phone)
            if user.verifyCode == verifyCode:
                user.verifyCode = None
                user.last_login = timezone.now()
                user.is_verified = True
                user.save()
                refresh = RefreshToken.for_user(user)
                login(request, user)
                return Response({"refresh" : str(refresh),"access":str(refresh.access_token)}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "Invalid verifyCode OR No any active user found for given verifyCode"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"message" : "No user with this phone!!"}, status=status.HTTP_400_BAD_REQUEST)


class RegisterApi(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args,  **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        password = serializer.validated_data['password']
        try:
            user = User.objects.get(phone=phone)
            if user.is_verified:
                auth_user = auth.authenticate(phone=phone, password=password)
                if auth_user:
                    auth.login(request, auth_user)
                    refresh = RefreshToken.for_user(user)
                    return Response({"refresh" : str(refresh),"access":str(refresh.access_token)}, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "message": "error, Wrong password",
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                verifyCode = helper.verifyCode_generator()
                helper.send_verifyCode(phone, verifyCode)
                user.verifyCode = verifyCode
                user.verifyCode_create_time = timezone.now
                user.save()
                return Response({
                    "message": "Ok, verify it"
                }, status=201)
        except User.DoesNotExist:
            user = User.objects.create_user(phone=phone, password=password)
            verifyCode = helper.verifyCode_generator()
            helper.send_verifyCode(phone, verifyCode)
            user.verifyCode = verifyCode
            user.verifyCode_create_time = timezone.now
            user.save()
            return Response({
                    "message": "Ok, verify it",
            }, status=status.HTTP_201_CREATED)


class VerifyPhoneApi(generics.GenericAPIView):
    serializer_class = PhoneSerializer

    def post(self, request, *args,  **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        try:
            user = User.objects.get(phone=phone)
            verifyCode = helper.verifyCode_generator()
            helper.send_verifyCode(phone, verifyCode)
            user.verifyCode = verifyCode
            user.verifyCode_create_time = timezone.now
            user.save()
            return Response({
                    "message": "Ok, verify it",
            }, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({
                    "message": "error, user with this phone number does not exist.",
            }, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordApi(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args,  **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data['password']
        if request.user.is_authenticated:
            user = request.user
            user.set_password(password)
            user.save()
            return Response({
                    "message": "Ok, your password changed.",
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                    "message": "error, please login and try it again.",
            }, status=status.HTTP_401_UNAUTHORIZED)
   