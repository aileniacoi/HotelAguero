from django.shortcuts import render
from django.http import HttpResponse
from .models import Habitacion, Cliente, Reserva, ListaPrecio, MovimientoCaja, DetalleListaPrecio

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from .forms import ClienteForm, HabitacionForm, ReservaForm, CajaForm, ListaPrecioForm, DetalleListaPrecioForm, ListaPrecioDetalleInlineFormset

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
    context = {'habitaciones': habitaciones}
    return render(request, 'listHabitaciones.html', context)


def detHabitacion(request, id):
    habitacion = Habitacion.objects.filter(id=id).first()
    context = {'habitacion': habitacion}
    return render(request, 'habitacionform.html', context)


class HabitacionBajaView(SuccessMessageMixin, DeleteView):
    model = Habitacion
    template_name = 'habitacionbaja.html'
    success_url = '/habitaciones'
    success_message = 'La habitación fue eliminada.'


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
                                                   "form": form,})


def clientes(request):
    clientes = Cliente.objects.all()
    context = {'clientes': clientes, }
    return render(request, 'listClientes.html', context)


# class ClienteNuevoView(FormView):
#     template_name = 'clienteForm.html'
#     form_class = ClienteForm
#     success_message = "Cliente agregado correctamente"
#
#     def form_valid(self, form):
#         form.save()
#         return super().form_valid(form)
#
# class FormSuccessView(View):
#         def get(self, request, *args, **kwargs):
#             return HttpResponse("Cliente grabado exitosamente")


class ClienteBajaView(SuccessMessageMixin, DeleteView):
    model = Cliente
    template_name = 'clientebaja.html'
    success_url = '/clientes'
    success_message = 'El cliente fue eliminado.'

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
    return render(request, "clienteForm.html", {"method": request.method, "form": form, })


def reservas(request):
    reservas = Reserva.objects.all()
    context = {'reservas': reservas, }
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
    return render(request, "reservasForm.html", {"method": request.method, "form": form, })


def listasPrecio(request):
    listas = ListaPrecio.objects.all()
    context = {'listas': listas, }
    return render(request, 'listPrecios.html', context)


def listaPrecio_edit(request, pk=None):
    if pk is not None:
        lista = get_object_or_404(ListaPrecio, pk=pk)
        detalle = DetalleListaPrecio.objects.filter(idListaPrecio=lista)
    else:
        lista = None
        detalle = ListaPrecioDetalleInlineFormset(queryset=ListaPrecio.objects.none())

    if request.method == "POST":
        t_form = ListaPrecioForm(request.POST, instance=lista)
        if t_form.is_valid():
            updated_lista = t_form.save()

            i_formset = ListaPrecioDetalleInlineFormset(request.POST, instance=lista)

            if i_formset.is_valid():
                i_formset.save()

            if lista is None:
                 messages.success(request, "La lista de precio fue creada.".format(updated_lista))
            else:
                 messages.success(request, "La lista de precio fue modificada.".format(updated_lista))
            return redirect("/listasprecio/viewdetail/" + str(updated_lista.pk), listaPrecio_edit)
    else:
        t_form = ListaPrecioForm(instance=lista)
        i_formset = ListaPrecioDetalleInlineFormset(instance=lista)
        i_formset.extra = 1 if i_formset.queryset.count() < 1 else 0

    return render(request, "preciosform.html", {"method": request.method, "t_form": t_form, 'i_formset': i_formset})



def ListaPrecioCreateView(request):
    template_name = 'preciosform.html'
    if request.method == 'GET':
        t_form = ListaPrecioForm(request.GET or None)
        i_formset = ListaPrecioDetalleInlineFormset(queryset=ListaPrecio.objects.none())
    elif request.method == 'POST':
        t_form = ListaPrecioForm(request.POST)
        if t_form.is_valid():
            t = t_form.save(commit=False)
            t.save()

            i_formset = ListaPrecioDetalleInlineFormset(request.POST, instance=t)
            if i_formset.is_valid():
                i_formset.save()
                messages.success(request, 'La lista de precio fue creada.'.format(t))

                return redirect('/listasprecio/viewdetail/', pk=t.pk)

    return render(request, template_name, {
        't_form': t_form,
        'i_formset': i_formset,
    })


# def updateListaPrecio(request, pk):
#     template_name = 'preciosform.html'
#     t = get_object_or_404(ListaPrecio, pk=pk)
#     i = DetalleListaPrecio.objects.filter(idListaPrecio=t)
#     if request.method == 'GET':
#         t_form = ListaPrecioForm(instance=t)
#         i_formset = ListaPrecioDetalleInlineFormset(instance=t)
#         i_formset.extra = 1 if i_formset.queryset.count() < 1 else 0
#     elif request.method == 'POST':
#         t_form = ListaPrecioForm(request.POST, instance=t)
#         if t_form.is_valid():
#             t_form.save()
#             i_formset = ListaPrecioDetalleInlineFormset(request.POST, instance=t)
#             if i_formset.is_valid():
#                 i_formset.save()
#                 messages.success(request, "La lista de precio fue modificada.".format(t_form))
#                 return redirect('modlistasPrecio', pk=t.pk)
#
#     return render(request, template_name, {
#         't_form': t_form,
#         'i_formset': i_formset,
#         'i': i,
#         't': t,
#
#     })


def movimientosCaja(request):
    cajaMov = MovimientoCaja.objects.all()
    context = {'cajaMov': cajaMov, }
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
    return render(request, "cajaform.html", {"method": request.method, "form": form, })

