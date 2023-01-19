from django.urls import path
from user_auth import api

app_name = 'user_auth'

urlpatterns = [
    path('register', api.RegisterApi.as_view(), name="register"),
    path('verifycode', api.VerifyApi.as_view(), name="verify"),
    path('resetpassword', api.ResetPasswordApi.as_view(), name="verify"),
    path('verifyphone', api.VerifyPhoneApi.as_view(), name="verify"),
    path('rud/<int:pk>', api.UserRUD.as_view(), name="rud_user"),
    # # bank gateway
    # path('gateway/', api.GoToGatewayShop.as_view()),
    # path('callback/', api.CallbackGatewayShop.as_view(), name='callback'),
]
