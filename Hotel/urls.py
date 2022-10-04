from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='vInicio'),
    path('index/', views.index, name='index'),
    path('habitaciones/', views.habitaciones, name='habitaciones'),
    path('dethabitaciones/<int:id>/', views.detHabitacion, name='detalleHabitacion'),
    path('clientes/', views.clientes),
    path('reservas/', views.reservas)
]
