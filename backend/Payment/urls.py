from django.urls import path , include
from django.conf import settings
from Bike_Info.views import *
from django.conf.urls.static import static
urlpatterns = [
        
]+  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
