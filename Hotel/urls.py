from django.urls import path
from . import views

urlpatterns = [
    path('vista1/', views.bienvenidos, name='vBienvenidos'),
    path('habitaciones/', views.habitaciones, name='habitaciones'),
    path('dethabitaciones/<int:id>/', views.detHabitacion, name='detalleHabitacion')
]
