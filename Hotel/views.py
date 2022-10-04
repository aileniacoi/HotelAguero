from django.shortcuts import render
from django.http import HttpResponse
from .models import Habitacion, Cliente, Reserva, ListaPrecio

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .forms import ClienteForm

from django.views.generic.edit import FormView, UpdateView, DeleteView, CreateView
from django.views.generic import DetailView
from django.views import View


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
    context = {'habitaciones': habitaciones, 'title': 'Habitaciones'}
    return render(request, 'listHabitaciones.html', context)


def detHabitacion(request, id):
    habitacion = Habitacion.objects.filter(id=id).first()
    context = {'habitacion': habitacion}
    return render(request, 'listHabitaciones.html', context)


def clientes(request):
    clientes = Cliente.objects.all()
    context = {'clientes': clientes, 'title': 'Clientes'}
    return render(request, 'listClientes.html', context)


class ClienteNuevoView(FormView):
    template_name = 'clienteForm.html'
    form_class = ClienteForm
    success_url = '/movexitoso'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class FormSuccessView(View):
        def get(self, request, *args, **kwargs):
            return HttpResponse("Cliente grabado exitosamente")


class ClienteModView(UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clienteForm.html'
    success_url = '/movexitoso'


class ClienteBajaView(DeleteView):
    model = Cliente
    template_name = 'clienteBaja.html'
    success_url = '/movexitoso'


def reservas(request):
    reservas = Reserva.objects.all()
    context = {'reservas': reservas, 'title': 'Reservas'}
    return render(request, 'listReservas.html', context)


def listasPrecio(request):
    listas = ListaPrecio.objects.all()
    context = {'listas': listas, 'title': 'Listas de Precio'}
    return render(request, 'listPrecios.html', context)
