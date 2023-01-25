from rest_framework import serializers
from .models import Cliente, Habitacion, Reserva

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ('pk', 'nombreYApellido', 'dni', 'telefono')

class HabitacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habitacion
        fields = ('pk', 'numero', 'plazas')

class ReservaSerializer(serializers.ModelSerializer):
    idCliente = ClienteSerializer()
    idHabitacion = HabitacionSerializer()
    class Meta:
        model = Reserva
        fields = ('pk', 'fechaIngreso', 'fechaEgreso', 'idHabitacion', 'seniaSolicitada', 'idCliente')
