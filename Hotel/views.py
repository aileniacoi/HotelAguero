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


class SuccessMessageMixin:
    success_message = ''

    def form_valid(self, form):
        response = super().form_valid(form)
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data


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
    return render(request, 'habitacionform.html', context)


def clientes(request):
    clientes = Cliente.objects.all()
    context = {'clientes': clientes, 'title': 'Clientes'}
    return render(request, 'listClientes.html', context)


class ClienteNuevoView(SuccessMessageMixin, FormView):
    template_name = 'clienteForm.html'
    form_class = ClienteForm
    success_message = "Cliente agregado correctamente"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ClienteModView(SuccessMessageMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clienteForm.html'
    success_message = "Cliente actualizado correctamente"


class ClienteBajaView(DeleteView):
    model = Cliente
    template_name = 'clienteBaja.html'



class ClienteDetalleView(SuccessMessageMixin, DetailView):
    model = Cliente
    template_name = 'clienteForm.html'
    success_message = "Gracias...!"


def cliente_edit(request, pk=None):
    if pk is not None:
        cliente = get_object_or_404(Cliente, pk=pk)
    else:
        cliente = None
    if request.method == "POST":
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            updated_cliente = form.save()
            if cliente is None:
                 messages.success(request, "El cliente \"{}\" fue creado.".format(updated_cliente))
            else:
                 messages.success(request, "El cliente \"{}\" fue modificado.".format(updated_cliente))
            return redirect("/clientes/viewdetail/" + str(updated_cliente.pk), cliente_edit)
    else:
        form = ClienteForm(instance=cliente)
    return render(request, "clienteForm.html", {"method": request.method, "form": form})


def reservas(request):
    reservas = Reserva.objects.all()
    context = {'reservas': reservas, 'title': 'Reservas'}
    return render(request, 'listReservas.html', context)


def listasPrecio(request):
    listas = ListaPrecio.objects.all()
    context = {'listas': listas, 'title': 'Listas de Precio'}
    return render(request, 'listPrecios.html', context)
