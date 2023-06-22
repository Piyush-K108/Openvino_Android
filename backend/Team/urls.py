from django.urls import path , include
from django.conf import settings
from Team.views import *
from django.conf.urls.static import static
urlpatterns = [
        path('create_Team/',LoginTeamVIew),
     
        
]+  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
