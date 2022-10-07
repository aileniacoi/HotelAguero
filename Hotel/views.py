from django.shortcuts import render
from django.http import HttpResponse
from .models import Habitacion, Cliente, Reserva, ListaPrecio, MovimientoCaja, DetalleListaPrecio

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from .forms import ClienteForm, HabitacionForm, ReservaForm, CajaForm, ListaPrecioForm

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


def habitacion_edit(request, pk=None):
    if pk is not None:
        habitacion = get_object_or_404(Habitacion, pk=pk)
    else:
        habitacion = None
    if request.method == "POST":
        form = HabitacionForm(request.POST, instance=habitacion)
        if form.is_valid():
            updated_hab = form.save()
            if habitacion is None:
                 messages.success(request, "La habitación {} fue creada.".format(updated_hab))
            else:
                 messages.success(request, "La habitación {} fue modificada.".format(updated_hab))
            return redirect("/habitaciones/viewdetail/" + str(updated_hab.pk), habitacion_edit)
    else:
        form = HabitacionForm(instance=habitacion)
    return render(request, "habitacionform.html", {"method": request.method,
                                                   "form": form,
                                                   "title": "Habitacion"})



def clientes(request):
    clientes = Cliente.objects.all()
    context = {'clientes': clientes, 'title': 'Clientes'}
    return render(request, 'listClientes.html', context)


class ClienteNuevoView(FormView):
    template_name = 'clienteForm.html'
    form_class = ClienteForm
    success_message = "Cliente agregado correctamente"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class FormSuccessView(View):
        def get(self, request, *args, **kwargs):
            return HttpResponse("Cliente grabado exitosamente")


class ClienteModView(SuccessMessageMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clienteForm.html'
    success_message = "Cliente actualizado correctamente"


class ClienteBajaView(DeleteView):
    model = Cliente
    template_name = 'clienteBaja.html'


class ClienteDetalleView(DetailView):
    model = Cliente
    template_name = 'clienteForm.html'



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
    return render(request, "clienteForm.html", {"method": request.method, "form": form, "title": "Cliente"})


def reservas(request):
    reservas = Reserva.objects.all()
    context = {'reservas': reservas, 'title': 'Reservas'}
    return render(request, 'listReservas.html', context)


class ReservasDetalleView(DetailView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'reservasForm.html'


def reserva_edit(request, pk=None):
    if pk is not None:
        reserva = get_object_or_404(Reserva, pk=pk)
    else:
        reserva = None
    if request.method == "POST":
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            updated_reserva = form.save()
            if reserva is None:
                 messages.success(request, "La reserva \"{}\" fue creada.".format(updated_reserva))
            else:
                 messages.success(request, "La reserva \"{}\" fue modificada.".format(updated_reserva))
            return redirect("/reservas/viewdetail/" + str(updated_reserva.pk), reserva_edit)
    else:
        form = ReservaForm(instance=reserva)
    return render(request, "reservasForm.html", {"method": request.method, "form": form, "title": "Reserva"})


def listasPrecio(request):
    listas = ListaPrecio.objects.all()
    context = {'listas': listas, 'title': 'Listas de Precio'}
    return render(request, 'listPrecios.html', context)


def listaPrecio_edit(request, pk=None):
    if pk is not None:
        lista = get_object_or_404(ListaPrecio, pk=pk)
    else:
        lista = None
    if request.method == "POST":
        form = ListaPrecioForm(request.POST, instance=lista)
        if form.is_valid():
            updated_lista = form.save()
            if lista is None:
                 messages.success(request, "La lista de precio fue creada.".format(updated_lista))
            else:
                 messages.success(request, "La lista de precio fue modificada.".format(updated_lista))
            return redirect("/listasprecio/viewdetail/" + str(updated_lista.pk), listaPrecio_edit)
    else:
        form = ListaPrecioForm(instance=lista)
    return render(request, "preciosform.html", {"method": request.method, "form": form, "title": "Lista de precio"})


def manage_lista(request, pk):
    lista = ListaPrecio.objects.get(pk=pk)
    DetalleListaInlineFormSet = inlineformset_factory(ListaPrecio, DetalleListaPrecio, fields=['cantidadPersonas'])
    if request.method == "POST":
        formset = DetalleListaInlineFormSet(request.POST, request.FILES, instance=lista)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(lista.get_absolute_url())
    else:
        formset = DetalleListaInlineFormSet(instance=lista)
    return render(request, 'preciosform.html', {'formset': formset})


def movimientosCaja(request):
    cajaMov = MovimientoCaja.objects.all()
    context = {'cajaMov': cajaMov, 'title': 'Caja'}
    return render(request, 'listCaja.html', context)


def caja_edit(request, pk=None):
    if pk is not None:
        mov = get_object_or_404(MovimientoCaja, pk=pk)
    else:
        mov = None
    if request.method == "POST":
        form = CajaForm(request.POST, instance=mov)
        if form.is_valid():
            updated_mov = form.save()
            if mov is None:
                 messages.success(request, "El ingreso/egreso fue creado.".format(updated_mov))
            else:
                 messages.success(request, "El ingreso/egreso fue modificado.".format(updated_mov))
            return redirect("/movimientoscaja/viewdetail/" + str(updated_mov.pk), caja_edit)
    else:
        form = CajaForm(instance=mov)
    return render(request, "cajaform.html", {"method": request.method, "form": form, "title": "Caja"})

