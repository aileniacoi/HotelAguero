from django.urls import path

from . import views
from WebHotel.views import inicio2

urlpatterns = [
    path('inicio2', views.inicio2, name='inicio2'),
    path('index2', views.index2, name='index2'),
    path('conocenos', views.Conocenos, name='conocenos'),
    path('galeria', views.Galeria, name='galeria'),
    path('contacto', views.Contacto, name='contacto'),
]
