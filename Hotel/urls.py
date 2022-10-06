from django.urls import path
from . import views
from Hotel.views import ReservasDetalleView

urlpatterns = [
    path('', views.inicio, name='vInicio'),
    path('index/', views.index, name='index'),
    path('habitaciones/', views.habitaciones, name='habitaciones'),
    path('habitaciones/viewdetail/<int:id>/', views.detHabitacion, name='detalleHabitacion'),
    path('habitaciones/edit/<int:id>/', views.detHabitacion, name='detalleHabitacion'),
    path('clientes/', views.clientes),
    path('clientes/add/', views.ClienteNuevoView.as_view(), name='nuevoCliente'),
    path('clientes/edit/<int:pk>', views.ClienteModView.as_view(), name='modCliente'),
    path('reservas/', views.reservas),
    path('reservas/reservasdetail/<int:pk>/', ReservasDetalleView.as_view(), name='detalleReserva'),
    path('listasPrecio/', views.listasPrecio),

]
