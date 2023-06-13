from django.urls import path , include
from django.conf import settings
from accounts.views import *
from django.conf.urls.static import static
urlpatterns = [
    path('create_user/',CreateUserView),
    path('verify_otp/',VerifyOTP_View),
    path('resend_otp/',ResendOTP_View),
]+  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
