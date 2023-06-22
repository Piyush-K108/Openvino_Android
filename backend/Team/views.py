from django.http import JsonResponse
from requests import Response
from rest_framework.decorators import api_view
from accounts.helper import MessageHandler
from accounts.models import UserAccounts
import random , string
from accounts.serializers import *
from django.contrib.auth import authenticate , login

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

    if user:
        # Authenticate user
        authenticated_user = authenticate(request, phone=phone, password=password)

        if authenticated_user is not None:
            # Login the user
            login(request, authenticated_user)
            return JsonResponse({'message': 'Team login successful.'})
        else:
            return JsonResponse({'error': 'Invalid phone or password.'}, status=401)
    else:
        # Generate a random password
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=5))

        # Create a new user
        user = UserAccounts.objects.create_teamuser(name = name ,phone=phone, password=password)
        login(request, user)
        return JsonResponse({'message': 'Team account created and logged in successfully.', 'password': password})
