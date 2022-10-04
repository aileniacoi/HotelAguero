from django.contrib import admin
from Hotel.models import Habitacion, Cliente, Reserva, ListaPrecio, DetalleListaPrecio
from Hotel.models import MovimientoCaja

# Register your models here.


class AdminCliente(admin.ModelAdmin):
    list_display = ('nombreYApellido', 'dni', 'telefono')
    list_filter = ('nombreYApellido', 'dni')


class AdminReserva(admin.ModelAdmin):
    list_display = ('fechaIngreso', 'idCliente', 'idHabitacion')
    list_filter = ('fechaIngreso', 'idCliente')


class AdminListaPrecio(admin.ModelAdmin):
    list_display = ('vigenciaDesde', 'vigenciaHasta')


class AdminMovimientoCaja(admin.ModelAdmin):
    list_display = ('fecha', 'idConcepto', 'monto')
    list_filter = ('fecha', 'idTipoMovimiento')


class AdminDetalleListaPrecio(admin.ModelAdmin):
    list_display = ('idListaPrecio', 'precioPorDia', 'cantidadPersonas')
    list_filter = ('idListaPrecio',)


admin.site.site_header = 'Hotel Agüero'
admin.site.site_title = 'Hotel Agüero'
admin.site.index_title = 'Reservas'

admin.site.register(Habitacion)
admin.site.register(Reserva, AdminReserva)
admin.site.register(Cliente, AdminCliente)
admin.site.register(ListaPrecio, AdminListaPrecio)
admin.site.register(DetalleListaPrecio, AdminDetalleListaPrecio)
admin.site.register(MovimientoCaja, AdminMovimientoCaja)
