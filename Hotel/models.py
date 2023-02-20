from django.db import models
from django.urls import reverse

# Create your models here.


class Habitacion(models.Model):
    """Habitaciones en alquiler"""
    numero = models.IntegerField()
    plazas = models.IntegerField()
    esPlantaBaja = models.BooleanField(verbose_name='Planta baja')
    habilitada = models.BooleanField()

    def __str__(self):
        return str(self.numero)


class Cliente(models.Model):
    """Clientes que reservaron en el hotel"""
    nombreYApellido = models.CharField(max_length=200, verbose_name='Nombre y apellido')
    dni = models.CharField(max_length=10, blank=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=15)
    direccion = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.nombreYApellido

    def get_absolute_url(self):
        return reverse('detailCliente', kwargs={'pk': self.pk})


class Reserva(models.Model):
    """Reservas realizadas"""
    fechaRegistro = models.DateField(verbose_name='Fecha de registro')
    fechaIngreso = models.DateField(verbose_name='Fecha de Ingreso')
    fechaEgreso = models.DateField(verbose_name='Fecha de Egreso')
    cantidadPersonas = models.IntegerField(verbose_name='Personas')
    idHabitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE, verbose_name='Habitación', null=True, blank=True)
    idCliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name='Cliente')
    seniaSolicitada = models.DecimalField(decimal_places=2, max_digits=10, null=True, verbose_name='Seña solicitada')
    precioTotal = models.DecimalField(decimal_places=2, max_digits=10, null=True, verbose_name='Precio total')
    precioPorDia = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Precio por día')
    incluyeDesayuno = models.BooleanField(verbose_name="Desayuno")
    porcentajeDescuento = models.IntegerField(null=True, blank=True, verbose_name='Porcentaje de descuento')
    importeDescuento = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True, verbose_name='Importe de descuento')
    descuentoPorPorcentaje = models.BooleanField(null=True, verbose_name='Descuento por porcentaje')
    observaciones = models.TextField(max_length=500, blank=True)
    fechaCancelacion = models.DateField(verbose_name='Fecha de Cancelacion', null=True, blank=True)


    def __str__(self):
        return f'{self.pk} - {self.idCliente}'


class ListaPrecio(models.Model):
    """Listas de precios"""
    TEMPORADABAJA = 'TB'
    TEMPORADAMEDIA = 'TM'
    TEMPORADAALTA = 'TA'
    TIPOLISTA = [
        (TEMPORADAALTA, 'Temporada Alta'),
        (TEMPORADAMEDIA, 'Temporada Media'),
        (TEMPORADABAJA, 'Temporada Baja'),
    ]
    vigenciaDesde = models.DateField(verbose_name='Vigencia desde')
    vigenciaHasta = models.DateField(verbose_name='Vigencia hasta',)
    idTipoLista = models.CharField(choices=TIPOLISTA, verbose_name='Tipo de lista', max_length=3)
    
    def __str__(self):
        return f'{self.vigenciaDesde} - {self.vigenciaHasta}'


class DetalleListaPrecio(models.Model):
    """Detalle en listas de precio"""
    cantidadPersonas = models.IntegerField(verbose_name='Cantidad de personas')
    precioPorDia = models.DecimalField(verbose_name='Precio por día', decimal_places=2, max_digits=10)
    idListaPrecio = models.ForeignKey(ListaPrecio, on_delete=models.CASCADE)
    
    def __str__(self):
        return f'{self.cantidadPersonas} pers. - $ {self.precioPorDia}'


class MovimientoCaja(models.Model):
    """Movimientos de caja"""
    INGRESO = 'IN'
    EGRESO = 'EG'
    TIPOMOVIMIENTO = [
        (INGRESO, 'Ingreso'),
        (EGRESO, 'Egreso'),
    ]
    SENIA = 'SEN'
    SALDO = 'SAL'
    GASTOSVARIOS = 'GVS'
    LAVADERO = 'LAV'
    PANADERIA = 'PAN'
    DEVOLUCION = 'DEV'
    CONCEPTO = [
        (SENIA, 'Seña'),
        (SALDO, 'Saldo'),
        (GASTOSVARIOS, 'Gastos varios'),
        (LAVADERO, 'Lavadero'),
        (PANADERIA, 'Panaderia'),
        (DEVOLUCION, 'Devolución'),
    ]
    CREDITO = 'CRE'
    DEBITO = 'DEB'
    EFECTIVO = 'EFE'
    TRANSFERENCIA = 'TRA'
    FORMAPAGO = [
        (CREDITO, 'Credito'),
        (DEBITO, 'Debito'),
        (EFECTIVO, 'Efectivo'),
        (TRANSFERENCIA, 'Transferencia')
    ]
    idTipoMovimiento = models.CharField(choices=TIPOMOVIMIENTO, verbose_name='Tipo de movimiento', max_length=3)
    idConcepto = models.CharField(choices=CONCEPTO, verbose_name='Concepto', max_length=3)
    idFormaPago = models.CharField(choices=FORMAPAGO, verbose_name='Forma de pago', max_length=3)
    fecha = models.DateField()
    monto = models.IntegerField()
    numeroComprobante = models.CharField(max_length=50, verbose_name='Número de comprobante', blank=True)
    idReserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, verbose_name='Reserva', blank=True, null=True)

    def __str__(self):
        return str(self.monto)
