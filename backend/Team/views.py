from django.http import JsonResponse
from requests import Response
from rest_framework.decorators import api_view
from accounts.helper import MessageHandler
from accounts.models import UserAccounts
import random , string
from accounts.serializers import *
from django.contrib.auth import  login

def authenticate(request, name, phone, password):
        try:
            user = UserAccounts.objects.get(name=name, phone=phone,password=password)
            return user
        except UserAccounts.DoesNotExist:
            pass
        return None

@api_view(['POST'])
def LoginTeamVIew(request):
    phone = request.data.get('phone')
    name = request.data.get('name')
    password  =request.data.get('password')

    # Validate request data
    if not phone :
        return Response({'error': 'Phone is required.'}, status=400)

    # Check if the user already exists
    user = UserAccounts.objects.filter(phone=phone,name=name).first()
    # Generate a random password
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=5))

    # Create a new user
    UserAccounts.objects.create_teamuser(name = name ,phone=phone, password=password)
    return JsonResponse({'message': 'Team account created and logged in successfully.', 'password': password})


@api_view(['POST'])
def VerifyTeamView(request):
    phone = request.data.get('phone')
    name = request.data.get('name')
    password = request.data.get('password')

    # Validate request data
    if not phone or not name or not password:
        return JsonResponse({'error': 'Phone, name, and password are required.'}, status=400)

    authenticated_user = authenticate(request, name=name, phone=phone, password=password)
    if authenticated_user is not None:
        # Login the user
        login(request, authenticated_user)
        user_account = UserAccounts.objects.filter(phone=phone).first()
        if user_account is not None:
            return JsonResponse({'message': 'Team login successful.', 'uid': user_account.uid})
        else:
            return JsonResponse({'error': 'User account not found.'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid phone or password.'}, status=401)
