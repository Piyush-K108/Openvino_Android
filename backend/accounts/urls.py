from django.urls import path , include
from django.conf import settings
from accounts.views import *
from django.conf.urls.static import static
urlpatterns = [
        path('create_user/',CreateUserView),
        path('verify_otp/<str:uid>',VerifyOTP_View),
        path('resend_otp/',ResendOTP_View),
        path('EditProfile/<str:uid>/',EditProfileView.as_view()),
        path('Uplode_Profile/<str:uid>/',Uplode_ProfilePic.as_view())
        
]+  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
