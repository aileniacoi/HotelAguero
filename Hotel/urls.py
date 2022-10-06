from django.urls import path
from . import views
from Hotel.views import ReservasDetalleView

urlpatterns = [
    path('', views.inicio, name='vInicio'),
    path('index/', views.index, name='index'),
    path('habitaciones/', views.habitaciones, name='habitaciones'),
    path('habitaciones/add/', views.detHabitacion, name='newHabitacion'),
    path('habitaciones/viewdetail/<int:id>/', views.detHabitacion, name='detailHabitacion'),
    path('habitaciones/edit/<int:id>/', views.detHabitacion, name='modHabitacion'),
    path('clientes/', views.clientes),
    path('clientes/add/', views.cliente_edit, name='newCliente'),
    path('clientes/edit/<int:pk>', views.cliente_edit, name='modCliente'),
    path('clientes/viewdetail/<int:pk>', views.cliente_edit, name='detailCliente'),
    path('clientes/delete/<int:pk>', views.ClienteModView.as_view(), name='detailCliente'),
    path('reservas/', views.reservas),
    path('reservas/reservasdetail/<int:pk>/', ReservasDetalleView.as_view(), name='detalleReserva'),
    path('listasPrecio/', views.listasPrecio),

]
