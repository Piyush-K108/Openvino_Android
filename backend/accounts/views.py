from django.http import JsonResponse
from django.shortcuts import render
from requests import Response
from rest_framework.decorators import api_view
from accounts.helper import MessageHandler
from accounts.models import UserAccounts
import random
from accounts.serializers import *
from rest_framework import generics,status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView

@api_view(['POST'])
def CreateUserView(request):
    data = request.data
    phone = "+91"+data.get('phone')

    if not phone:
        return Response({"error": "Phone number is required."}, status=400)

    # Check if the user already exists
    if UserAccounts.objects.filter(phone=phone).exists():
        return Response({"error": "User with the provided phone number already exists."}, status=400)

    # Create the user
    user = UserAccounts.objects.create_user(phone=phone)

    # Send OTP
    user.otp = random.randint(100000, 999999)
    
    message_handler = MessageHandler(phone, user.otp).set_otp()
    user.save()
    # print(message_handler)
    return JsonResponse({"uid":user.uid})




@api_view(['POST'])
def VerifyOTP_View(request,uid):
    data = request.data
    uid = uid
    otp = data.get('otp')
    print(uid)
    if not uid or not otp:
        return JsonResponse({"error": "uid number and OTP are required."}, status=400)

    profile = UserAccounts.objects.filter(uid=uid).first()
    if not profile:
        return JsonResponse({"error": "User profile not found."}, status=404)

    if profile.otp == otp:
        # OTP is valid, you can perform the desired actions here
        profile.is_active = True
        profile.save()
        return JsonResponse({"message": "OTP verification successful."})

    return JsonResponse({"error": "Invalid OTP."}, status=400)

@api_view(['POST'])
def ResendOTP_View(request):
    data = request.data
    phone = data.get('phone')

    if not phone:
        return JsonResponse({"error": "Phone number is required."}, status=400)

    profile = UserAccounts.objects.filter(phone=phone).first()
    if not profile:
        return JsonResponse({"error": "User profile not found."}, status=404)

    profile.otp = random.randint(100000, 999999)
    profile.save()
    message_handler = MessageHandler(phone, profile.otp).set_otp()

    return JsonResponse({"message": "New OTP sent successfully."})

class EditProfileView(APIView):
    def put(self, request, uid):
        profile = UserAccounts.objects.filter(uid=uid).first()
        if not profile:
            return Response({"error": "User profile not found."}, status=404)

        # Update the profile fields based on the provided data
        profile.name = request.data.get('name', profile.name)
        profile.email = request.data.get('email', profile.email)
        profile.Country = request.data.get('Country', profile.Country)
        profile.State = request.data.get('State', profile.State)
        profile.City = request.data.get('City', profile.City)
        profile.Date_of_Birth = request.data.get('Date_of_Birth', profile.Date_of_Birth)

        # Save the profile
        profile.save()

        # Return a success response
        return JsonResponse({"message": "Profile updated successfully."})
    

class Uplode_ProfilePic(generics.UpdateAPIView):
    serializer_class = UserAccountsSerializer
    parser_classes = (MultiPartParser, FormParser)
    lookup_field = 'uid'

    def get_queryset(self):
        return UserAccounts.objects.filter(uid=self.kwargs['uid'])

    def put(self, request, *args, **kwargs):
        profile = self.get_object()
        profile.ProfilePic = request.data.get('ProfilePic')
        profile.save()
        serializer = self.serializer_class(profile)
        return JsonResponse(serializer.data)
