from django.shortcuts import render
from django.http import HttpResponse
from .models import Habitacion, Cliente, Reserva


# Create your views here.


def inicio(request):
    cantidad = Habitacion.objects.count()
    context = {'cantidad': cantidad}
    return render(request, 'base.html', context)

def index(request):
    context = {}
    return render(request, 'index.html', context)


def habitaciones(request):
    habitaciones = Habitacion.objects.all()
    context = {'habitaciones': habitaciones}
    return render(request, 'listHabitaciones.html', context)


def detHabitacion(request, id):
    habitacion = Habitacion.objects.filter(id=id).first()
    context = {'habitacion': habitacion}
    return render(request, 'listHabitaciones.html', context)


def clientes(request):
    clientes = Cliente.objects.all()
    context = {'clientes': clientes}
    return render(request, 'listClientes.html', context)


def reservas(request):
    reservas = Reserva.objects.all()
    context = {'reservas': reservas}
    return render(request, 'listReservas.html', context)
