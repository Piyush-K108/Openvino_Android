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

UserAccounts = get_user_model()

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
        return HttpResponseBadRequest("User with the specified phone number does not exist.")

    # Assuming the phone number is the unique identifier for the user
    user = get_object_or_404(UserAccounts.objects, phone=phone)
    ev = request.data.get('EV')
    adhar_card = request.data.get('Adhar_Card')['uri']
    adhar_card_name = request.data.get('Adhar_Card')['name']
    license_Id = request.data.get('license_id')['uri']
    license_Id_name = request.data.get('license_id')['name']
    adhar_content = ContentFile(adhar_card)
    license_content = ContentFile(license_Id)
    print(ev,adhar_card)
    if ev:
        user.Adhar_Card.save(adhar_card_name, adhar_content, save=True)
    else:
        user.Adhar_Card.save(adhar_card_name, adhar_content, save=True)
        user.license_id.save(license_Id_name, license_content, save=True)
        

    return JsonResponse({"data":user.name})


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

    # Update the bike information
    serializer = BikeassignSerializer(bike, data=request.data)
    if serializer.is_valid():
        serializer.save()
    else:
        return HttpResponseBadRequest("Invalid bike data.")

    bike.is_assigned = True
    bike.save()

    # Create a rental record
    rental = Rental.objects.create(user=user, bike=bike)

    return JsonResponse({f'Bike assigned to {user.pk} successfully.': serializer.data})



@api_view(['PUT'])
def deassign_bike(request, phone):
    try:
        # Assuming the phone number is the unique identifier for the user
        user = UserAccounts.objects.get(phone=phone)
    except UserAccounts.DoesNotExist:
        return HttpResponseBadRequest("User with the specified phone number does not exist.")
 
    # Assuming the phone number is the unique identifier for the user
    user = get_object_or_404(UserAccounts.objects, phone=phone)

    # Fetch the bike information (e.g., by filtering assigned bikes)
    bike = Bike_Info.objects.filter(is_assigned=True).order_by('?').first()
    if not bike:
        return HttpResponseBadRequest("No assigned bike found.")

    # Update the bike's assignment status
    bike.is_assigned = False
    bike.save()

    # Delete the rental record for the user
    rental = Rental.objects.filter(user=user, bike=bike).first()
    if rental:
        rental.delete()

    # Serialize the bike information
    serializer = BikeDropSerializer(bike)
    if serializer.is_valid():
        serializer.save()
    else:
        return HttpResponseBadRequest("Invalid bike data.")

    # Include the serialized bike information in the response
    return JsonResponse({'message': 'Bike deassigned successfully.', 'bike': serializer.data})



