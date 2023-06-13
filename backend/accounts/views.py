from django.http import JsonResponse
from django.shortcuts import render
from requests import Response
from rest_framework.decorators import api_view
from accounts.helper import MessageHandler
from accounts.models import UserAccounts
import random

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
    return JsonResponse({"message": "User created successfully. OTP sent."})




@api_view(['POST'])
def VerifyOTP_View(request):
    data = request.data
    phone = data.get('phone')
    otp = data.get('otp')

    if not phone or not otp:
        return JsonResponse({"error": "Phone number and OTP are required."}, status=400)

    profile = UserAccounts.objects.filter(phone=phone).first()
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