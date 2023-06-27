from django.urls import path , include
from django.conf import settings
from Bike_Info.views import *
from django.conf.urls.static import static
urlpatterns = [
        path('assign_bike_to_user/<str:phone>/', assign_bike_to_user, name='assign_bike_user'),
        path('assign_bike_to_bike/<str:phone>/', assign_bike_to_bike, name='assign_bike_bike'),
        path('deassign_bike/<str:phone>/', deassign_bike, name='deassign_bike'),
        path('Create/',createBike)
]+  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
