from django.shortcuts import render
from django.http import HttpResponse
from .models import Habitacion


# Create your views here.


def bienvenidos(request):
    cantidad = Habitacion.objects.count()
    context = {'cantidad': cantidad}
    return render(request, 'index.html', context)


def habitaciones(request):
    habitaciones = Habitacion.objects.all()
    context = {'habitaciones': habitaciones}
    return render(request, 'listHabitaciones.html', context)


def detHabitacion(request, id):
    habitacion = Habitacion.objects.filter(id=id).first()
    context = {'habitacion': habitacion}
    return render(request, 'listHabitaciones.html', context)
