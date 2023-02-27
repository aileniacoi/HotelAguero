from rest_framework import serializers
from .models import Cliente, Habitacion, Reserva, MovimientoCaja

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ('pk', 'nombreYApellido', 'dni', 'telefono', 'direccion', 'email')

class HabitacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habitacion
        fields = ('pk', 'numero', 'plazas')

class CajaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimientoCaja
        fields = ('pk', 'monto')

class ReservaSerializer(serializers.ModelSerializer):
    total_pagos = serializers.SerializerMethodField()
    fechaIngreso = serializers.SerializerMethodField()
    fechaEgreso = serializers.SerializerMethodField()
    fechaRegistro = serializers.SerializerMethodField()

    idCliente = ClienteSerializer()
    idHabitacion = HabitacionSerializer()
    class Meta:
        model = Reserva
        fields = ('pk', 'fechaIngreso', 'fechaEgreso', 'idHabitacion', 'precioTotal', 'idCliente', 'cantidadPersonas',
                  'total_pagos', 'fechaRegistro')

    def get_total_pagos(self, obj):
        pagos = MovimientoCaja.objects.filter(idReserva=obj)
        total = sum(pago.monto for pago in pagos)
        return total

    def get_fechaIngreso(self, obj):
        return obj.fechaIngreso.strftime('%d/%m/%Y')

    def get_fechaEgreso(self, obj):
        return obj.fechaEgreso.strftime('%d/%m/%Y')

    def get_fechaRegistro(self, obj):
        return obj.fechaRegistro.strftime('%d/%m/%Y')