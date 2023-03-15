from django.urls import path
from . import views
from Hotel.views import ReservasDetalleView, ReporteReservasPDF, HabitacionesDisponiblesView, HabitacionesView, \
    ClientesView, ReservasView, ListaPrecioView, MovimientosCajaView, ReporteReservasCalendarioPDF, ListaPrecioBajaView, \
    CajaBajaView, helppage

app_name = "Hotel"
urlpatterns = [
    #path('', views.inicio, name='vInicio'),
    path('', views.index, name='index'),

    #HABITACIONES
    #path('habitaciones/', views.habitaciones, name='habitaciones'),
    path('habitaciones/', HabitacionesView.as_view(), name='habitaciones'),
    path('habitaciones/add/', views.habitacion_edit, name='newHabitacion'),
    path('habitaciones/viewdetail/<int:pk>/', views.habitacion_edit, name='detailHabitacion'),
    path('habitaciones/edit/<int:pk>/', views.habitacion_edit, name='modHabitacion'),
    path('habitaciones/delete/<int:pk>/', views.HabitacionBajaView.as_view(), name='deleteHabitacion'),
    path('habitacionesmensaje/', views.habitacionesmensaje, name='habitacionesmensaje'),
    path('api/habitaciones/disponibles/', HabitacionesDisponiblesView.as_view()),

    #CLIENTES
    #path('clientes/', views.clientes, name='clientes'),
    path('clientes/', views.ClientesView.as_view(), name='clientes'),
    path('clientes/add/', views.cliente_edit, name='newCliente'),
    path('clientes/edit/<int:pk>/', views.cliente_edit, name='modCliente'),
    path('clientes/editreserva/<int:pk>/', views.cliente_edit_reserva, name='modResCliente'),
    path('clientes/viewdetail/<int:pk>/', views.cliente_edit, name='detailCliente'),
    path('clientes/delete/<int:pk>/', views.ClienteBajaView.as_view(), name='deleteCliente'),
    path('clientemensaje/', views.clientemensaje, name='clientemensaje'),

    #RESERVAS
    #path('reservas/', views.reservas, name='reservas'),
    path('reservas/', views.ReservasView.as_view(), name='reservas'),
    path('reservas/calendar/<int:mes>/<int:anio>/', views.reservasCalendario, name='reservasCalendario'),
    #path('reservas/add/', views.reserva_edit, name='newReserva'),
    path('reservas/add/', views.alta_reserva, name='nuevaReserva'),
    path('reservas/edit/<int:pk>/', views.edit_reserva, name='reservaEdit'),
    #path('reservas/edit/<int:pk>/', views.reserva_edit, name='modReserva'),
    path('reservas/viewdetail/<int:pk>/', ReservasDetalleView.as_view(), name='detalleReserva'),
    path('reservas/delete/<int:pk>/', ReservasDetalleView.as_view(), name='deleteReserva'),
    path('reservas/cancel/<int:pk>/', views.cancelar_reserva, name='deleteReserva'),


    #LISTAS DE PRECIO
    path('listasprecio/', views.ListaPrecioView.as_view(), name='listasPrecio'),
    path('listasprecio/calendar/<int:mes>/<int:anio>/', views.preciosCalendario, name='preciosCalendario'),
    path('listasprecio/add/', views.listaPrecio_edit, name='newPrecio'),
    path('listasprecio/edit/<int:pk>/', views.listaPrecio_edit, name='modlistasPrecio'),
    path('listasprecio/viewdetail/<int:pk>/', views.listaPrecio_edit, name='deleteListasPrecio'),
    path('listasprecio/delete/<int:pk>/', views.ListaPrecioBajaView.as_view(), name='listasPrecio'),


    #CAJA
    path('movimientoscaja/', views.MovimientosCajaView.as_view(), name='movimientosCaja'),
    path('movimientoscaja/add/', views.caja_edit, name="newCaja"),
    path('movimientoscaja/edit/<int:pk>/', views.caja_edit, name="modCaja"),
    path('movimientoscaja/viewdetail/<int:pk>/', views.caja_edit, name="detalleCaja"),
    path('movimientoscaja/delete/<int:pk>/', views.CajaBajaView.as_view(), name="cajaBaja"),
    path('cajamensaje/', views.cajamensaje, name='cajamensajemensaje'),
    path('reservas/add/pagos/<int:reserva_id>/', views.agregar_pago_reserva, name='agregar_pago_reserva'),


    #SOLICITUDES
    path('get_precio/', views.get_price, name='get_price'),
    path('buscarreservacliente/', views.BuscarReservaCliente, name='buscarReservaCliente'),

    #REPORTES
    path('reporte_reservas_pdf/', ReporteReservasPDF.as_view(), name="reporte_reservas_pdf"),
    path('reporte_caja_pdf/', views.ReporteCajaPDF, name="reporte_caja_pdf"),
    path('calendario_reservas_pdf/<int:mes>/<int:anio>/', ReporteReservasCalendarioPDF, name="calendario_reservas_pdf"),

    #PAGINA DE AYUDA
    path('helppage/', views.helppage, name='helppage'),

    #PAGINA DE PERFIl
    #path('profile/', views.profile, name='profile')
]
