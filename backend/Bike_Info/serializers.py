from rest_framework import serializers
from .models import Bike_Info
from accounts.models import UserAccounts
class BikeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bike_Info
        fields = ['Electrical','KM_Previous','license_plate']

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccounts
        fields = '__all__'

class BikeassignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bike_Info
        fields = ['Pic_before','Estimated_Amount','KM_Previous']



class BikeDropSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bike_Info
        fields = ['Condition','KM_Later','Pic_after','Exact_Amount','Payed','Mode_of_Payment']