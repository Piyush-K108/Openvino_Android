import json
from datetime import datetime, timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from Bike_Info.models import Bike_Info, Rental
from .serializers import *
from django.http import HttpResponseBadRequest, JsonResponse
from rest_framework.response import Response 
from rest_framework import generics,status
from django.core.files.base import ContentFile
from rest_framework.parsers import MultiPartParser, FormParser
import base64
UserAccounts = get_user_model()
import numpy as np
import cv2

@api_view(['POST'])
def createBike(request):
    if request.method == 'POST':
        serializer = BikeInfoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        else:
            return JsonResponse(serializer.errors)
    else:
        return HttpResponseBadRequest()


@api_view(['PUT'])
def assign_bike_to_user(request, phone):
    try:
        # Assuming the phone number is the unique identifier for the user
        user = UserAccounts.objects.get(phone=phone)
    except UserAccounts.DoesNotExist:
        user = UserAccounts.objects.create_user(phone=phone)
        user.is_active = True
        user.save()
    # Assuming the phone number is the unique identifier for the user
    user = get_object_or_404(UserAccounts.objects, phone=phone)
    
    rental = Rental.objects.filter(user=user, return_date=None).first()

    ev = request.data.get('EV')
    adhar_card = request.data.get('Adhar_Card')
    # adhar_card1 = json.loads(adhar_card)
    # adhar_data = adhar_card1.get("data", "")

    if ev:   
        # adhar_content = ContentFile(base64.b64decode(adhar_data), name = user.name if user.name is not None else user.phone + 'AdharCard.jpg')
        user.Adhar_Card = adhar_card
        user.save()
    else:
        license = request.data.get('license_id')
        # license1 = json.loads(license)
        # license_data = license1.get("data", "")
        # license_content = ContentFile(base64.b64decode(license_data),  name = user.name if user.name is not None else user.phone + 'License_id.jpg')
        # adhar_content = ContentFile(base64.b64decode(adhar_data), name = user.name if user.name is not None else user.phone + 'AdharCard.jpg')
        user.Adhar_Card = adhar_card
        user.license_id = license
        user.save()
 
    serializer = UserUpdateSerializer(user)
    return Response(serializer.data)


@api_view(['PUT'])
def assign_bike_to_bike(request, phone):
    try:
        # Assuming the phone number is the unique identifier for the user
        user = UserAccounts.objects.get(phone=phone)
    except UserAccounts.DoesNotExist:
        return HttpResponseBadRequest("User with the specified phone number does not exist.")

    # Assuming the phone number is the unique identifier for the user
    user = get_object_or_404(UserAccounts.objects, phone=phone)
    # Fetch the bike information (e.g., by randomly selecting a bike)
    bike = Bike_Info.objects.filter(is_assigned=False).order_by('?').first()
    if not bike:
        return HttpResponseBadRequest("Bike not available for assignment.")
    Pic = request.data.get('Pic_before')
    # Pic_before = json.loads(Pic)
    # Pic_data = Pic_before.get("data", "")



    KM_Pic = request.data.get('KM_Reading')
    # KM_Pic = json.loads(KM_Pic)
    # KM_Pic = KM_Pic.get("data", "")
     
    # KM_Pic_content = ContentFile(base64.b64decode(KM_Pic), name=user.name+'Pic_Before.jpg')
    # KM_Pic = np.frombuffer(KM_Pic_content,np.int8)
    # cv2.imdecode(KM_Pic,cv2.IMREAD_COLOR)


    # Pic_content = ContentFile(base64.b64decode(Pic_data), name=user.name+'Pic_Before.jpg')
    bike.Pic_before = Pic
    bike.Estimated_Amount =  request.data.get('Estimated_Amount')
    bike.KM_Previous = request.data.get('KM_Previous')
    bike.is_assigned = True
    bike.save()

    # Create a rental record
    rental = Rental.objects.create(user=user, bike=bike)
    rental.rental_date = datetime.now()
    rental.return_date = None
    rental.save()
    serializer = BikeDropSerializer(rental)
    return JsonResponse({f'Bike assigned to {user.pk} successfully.': serializer.data})



@api_view(['PUT'])
def deassign_bike(request, phone):
    try:
        # Assuming the phone number is the unique identifier for the user
        user = UserAccounts.objects.get(phone=phone)
    except UserAccounts.DoesNotExist:
        return HttpResponseBadRequest("User with the specified phone number does not exist.")

    user = get_object_or_404(UserAccounts.objects, phone=phone)

    # Fetch the rental record for the user
    rental = Rental.objects.filter(user=user, return_date=None).first()
    if not rental:
        return HttpResponseBadRequest("No active rental found for the user.")

    # Fetch the bike assigned to the user
    bike = rental.bike

    # Update the bike's assignment status and other details
    Pic = request.data.get('Pic_after')
    Kilometer_now = request.data.get('KM_Now')
    Condition = request.data.get('Condition')
    Payed = request.data.get('Payed')
    Mode_of_Payment = request.data.get('Mode_of_Payment')
    ev = bike.Electrical

    # Pic_after = json.loads(Pic)
    # Pic_data = Pic_after.get("data", "")
    # Pic_content = ContentFile(base64.b64decode(Pic_data), name=f"{user.name}_Pic_after.jpg")

    bike.Pic_after = Pic
    old_datetime = rental.rental_date.replace(tzinfo=timezone.utc)  # Make the old datetime offset-aware
    new_datetime = datetime.now(timezone.utc)
    time_difference = new_datetime - old_datetime 
    if ev:
 # Calculate the difference between the old and new datetime
        minutes = int(time_difference.total_seconds() // 60)
        bike.Exact_Amount = (int(Kilometer_now) - int(bike.KM_Previous)) * 3 + minutes//2
    else:
        hours = int(time_difference.total_seconds() // 3600)
        bike.Exact_Amount = (hours) * 50
    if Condition == 'true':
        bike.Condition = True
    else:
        bike.Condition = False
    
    bike.Payed = True
    bike.Mode_of_Payment = Mode_of_Payment
    bike.KM_Now = Kilometer_now
    bike.is_assigned = False
    bike.save()

    # Update the return date in the rental record
    rental.return_date = datetime.now()
    rental.save()

    # Serialize the bike information
    serializer = BikeDropSerializer(rental)

    # Include the serialized bike information in the response
    return JsonResponse({'message': 'Bike deassigned successfully.', 'bike': serializer.data})




