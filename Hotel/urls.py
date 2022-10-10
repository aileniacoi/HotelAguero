from django.urls import path
from . import views
from Hotel.views import ReservasDetalleView

urlpatterns = [
    path('', views.inicio, name='vInicio'),
    path('index/', views.index, name='index'),
    path('habitaciones/', views.habitaciones, name='habitaciones'),
    path('habitaciones/add/', views.habitacion_edit, name='newHabitacion'),
    path('habitaciones/viewdetail/<int:pk>/', views.habitacion_edit, name='detailHabitacion'),
    path('habitaciones/edit/<int:pk>/', views.habitacion_edit, name='modHabitacion'),
    path('habitaciones/delete/<int:pk>/', views.HabitacionBajaView.as_view(), name='deleteHabitacion'),
    path('clientes/', views.clientes, name='clientes'),
    path('clientes/add/', views.cliente_edit, name='newCliente'),
    path('clientes/edit/<int:pk>/', views.cliente_edit, name='modCliente'),
    path('clientes/viewdetail/<int:pk>/', views.cliente_edit, name='detailCliente'),
    path('clientes/delete/<int:pk>/', views.ClienteBajaView.as_view(), name='deleteCliente'),
    path('reservas/', views.reservas, name='reservas'),
    path('reservas/add/', views.reserva_edit, name='newReserva'),
    path('reservas/edit/<int:pk>/', views.reserva_edit, name='modReserva'),
    path('reservas/viewdetail/<int:pk>/', ReservasDetalleView.as_view(), name='detalleReserva'),
    path('reservas/delete/<int:pk>/', ReservasDetalleView.as_view(), name='deleteReserva'),
    path('listasprecio/', views.listasPrecio, name='listasPrecio'),
    path('listasprecio/add/', views.ListaPrecioCreateView, name='newPrecio'),
    path('listasprecio/edit/<int:pk>/', views.listaPrecio_edit, name='modlistasPrecio'),
    path('listasprecio/viewdetail/<int:pk>/', views.listaPrecio_edit, name='deleteListasPrecio'),
    path('listasprecio/delete/<int:pk>/', views.listasPrecio, name='listasPrecio'),
    path('movimientoscaja/', views.movimientosCaja, name='movimientosCaja'),
    path('movimientoscaja/add/', views.caja_edit, name="newCaja"),
    path('movimientoscaja/edit/<int:pk>/', views.caja_edit, name="modCaja"),
    path('movimientoscaja/viewdetail/<int:pk>/', views.caja_edit, name="modCaja"),
    path('movimientoscaja/delete/<int:pk>/', views.listasPrecio),

]
