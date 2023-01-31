from django.shortcuts import render
from django.http import HttpResponse
from .models import Habitacion, Cliente, Reserva, ListaPrecio, MovimientoCaja, DetalleListaPrecio

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from .forms import ClienteForm, HabitacionForm, ReservaForm, CajaForm, ListaPrecioForm, DetalleListaPrecioForm, \
    ListaPrecioDetalleInlineFormset, PagosReservaInlineFormset
from .serializers import ReservaSerializer, HabitacionSerializer

from rest_framework.views import APIView
from rest_framework.response import Response

from django.views.generic.edit import FormView, UpdateView, DeleteView, CreateView
from django.views.generic import DetailView, View, ListView
from django.views import View
from django.urls import reverse
from django.db.models import Q, Sum

from django.conf import settings
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
import os
import json
from django.http import JsonResponse
from django.core import serializers
#from multi_form_view import MultiModelFormView

from datetime import datetime, date, time
import calendar

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
    hoy = datetime.now().date()

    ingresos = Reserva.objects.filter(fechaIngreso=hoy)
    egresos = Reserva.objects.filter(fechaEgreso=hoy)

    cantidadHabitaciones = Habitacion.objects.count()

    reservasActuales = Reserva.objects.filter(fechaIngreso__lte=hoy, fechaEgreso__gte=hoy)

    habitaciones_ocupadas = reservasActuales.values_list('idHabitacion', flat=True)
    habitaciones_disponibles = Habitacion.objects.exclude(id__in=habitaciones_ocupadas)

    context = {'ingresos': ingresos, 'egresos': egresos, 'cantidadHabitaciones':cantidadHabitaciones,
               'habitacionesDisponibles': habitaciones_disponibles }
    return render(request, 'index.html', context)


# ------ HABITACIONES ------

# def habitaciones(request):
#     habitaciones = Habitacion.objects.all()
#     context = {'habitaciones': habitaciones}
#     return render(request, 'listHabitaciones.html', context)

class HabitacionesView(ListView):
    template_name = 'listHabitaciones.html'
    model = Habitacion
    paginate_by = 10
    context_object_name = 'habitaciones'


# def detHabitacion(request, id):
#     habitacion = Habitacion.objects.filter(id=id).first()
#     context = {'habitacion': habitacion}
#     return render(request, 'habitacionform.html', context)


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


class HabitacionesDisponiblesView(APIView):
    def get(self, request):
        fecha_ingreso = request.GET.get('fecha_ingreso')
        fecha_egreso = request.GET.get('fecha_egreso')
        # habitaciones_ocupadas = Reserva.objects.filter(fechaIngreso__lte=fecha_egreso, fechaIngreso__gte=fecha_egreso)\
        #     .values_list('idHabitacion', flat=True)
        habitaciones_ocupadas = Reserva.objects.filter(Q(fechaIngreso__range=[fecha_ingreso, fecha_egreso]) |
                                                       Q(fechaIngreso__range=[fecha_ingreso, fecha_egreso]))\
            .values_list('idHabitacion', flat=True)
        habitaciones_disponibles = Habitacion.objects.exclude(id__in=habitaciones_ocupadas)
        serializer = HabitacionSerializer(habitaciones_disponibles, many=True)
        return Response(serializer.data)


# ------ CLIENTES ------


# def clientes(request):
#     clientes = Cliente.objects.all()
#     context = {'clientes': clientes, }
#     return render(request, 'listClientes.html', context)


class ClientesView(ListView):
    template_name = 'listClientes.html'
    model = Cliente
    paginate_by = 10
    context_object_name = 'clientes'


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


# ------ RESERVAS ------

# def reservas(request):
#     reservas = Reserva.objects.all()
#     context = {'reservas': reservas, }
#     return render(request, 'listReservas.html', context)

class ReservasView(ListView):
    template_name = 'listReservas.html'
    model = Reserva
    paginate_by = 10
    context_object_name = 'reservas'


def reservasCalendario(request, mes=None, anio=None):

    rangoFecha = calendar.monthrange(anio,mes)
    cantidadDias = rangoFecha[1]


    habitaciones = Habitacion.objects.all().order_by('numero')
    reservasQuery = Reserva.objects.filter(Q(fechaIngreso__month=mes, fechaIngreso__year=anio) |
                                           Q(fechaEgreso__month=mes, fechaEgreso__year=anio))
    reservas = ReservaSerializer(reservasQuery, many=True)

    context = {'reservas': json.dumps(reservas.data), 'habitaciones': habitaciones,
               'cantidadDias': range(1, cantidadDias + 1), 'mes': mes, 'anio': anio}
    return render(request, 'reservasCalendario.html', context)


class ReservasDetalleView(DetailView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'reservasForm.html'


# def edit_reserva(request, pk):
#     reserva = Reserva.objects.get(pk=pk)
#     cliente = Cliente.objects.get(pk=reserva.idCliente.pk)
#     if request.method == 'POST':
#         form_reserva = ReservaForm(request.POST, instance=reserva)
#         form_cliente = ClienteForm(request.POST, instance=cliente)
#         if form_reserva.is_valid() and form_cliente.is_valid():
#             form_reserva.save()
#             form_cliente.save()
#             return redirect('index')
#     else:
#         form_reserva = ReservaForm(instance=reserva)
#         form_cliente = ClienteForm(instance=cliente)
#     return render(request, 'reservaDetail.html', {'form_reserva': form_reserva, 'form_cliente': form_cliente})
#

def edit_reserva(request, pk):
    reserva = Reserva.objects.get(pk=pk)
    cliente = Cliente.objects.get(pk=reserva.idCliente.pk)
    pagos = MovimientoCaja.objects.filter(idReserva=reserva)
    if request.method == 'POST':
        form_reserva = ReservaForm(request.POST, instance=reserva)
        form_cliente = ClienteForm(request.POST, instance=cliente)
        if form_reserva.is_valid() and form_cliente.is_valid():
            form_reserva.save()
            form_cliente.save()
            return redirect('index')
    else:
        form_reserva = ReservaForm(instance=reserva)
        form_cliente = ClienteForm(instance=cliente)
        p_formset = PagosReservaInlineFormset(instance=reserva)
        pagosRealizados = pagos.aggregate(valor_total=Sum('monto'))['valor_total']
        saldo = reserva.precioTotal - pagosRealizados
    return render(request, 'reservaDetail.html', {'form_reserva': form_reserva, 'form_cliente': form_cliente, 'formset_pagos': p_formset,
                                                  'saldo': saldo})


def alta_reserva(request):
    reserva = None
    cliente = None
    if request.method == 'POST':
        form_reserva = ReservaForm(request.POST, instance=reserva)
        form_cliente = ClienteForm(request.POST, instance=cliente)

        print(form_reserva.errors)
        print(form_cliente.errors)
        if form_cliente.is_valid() and form_reserva.is_valid():
            cliente = form_cliente.save()
            reserva = form_reserva.save(commit=False)
            reserva.idCliente = cliente
            form_reserva.save()

            messages.success(request, "La reserva \"{}\" fue creada.".format(reserva))

            return redirect("")
            #return redirect("/reservas/edit/" + str(reserva.pk), edit_reserva())
    else:
        form_reserva = ReservaForm(instance=reserva)
        form_cliente = ClienteForm(instance=cliente)
    return render(request, 'nuevareserva.html', {'form_reserva': form_reserva, 'form_cliente': form_cliente})


# def reserva_edit(request, pk=None):
#     if pk is not None:
#         reserva = get_object_or_404(Reserva, pk=pk)
#     else:
#         reserva = None
#     if request.method == "POST":
#         form = ReservaForm(request.POST, instance=reserva)
#         if form.is_valid():
#             updated_reserva = form.save()
#             if reserva is None:
#                 messages.success(request, "La reserva \"{}\" fue creada.".format(updated_reserva))
#             else:
#                 messages.success(request, "La reserva \"{}\" fue modificada.".format(updated_reserva))
#             return redirect("/reservas/edit/" + str(updated_reserva.pk), reserva_edit)
#     else:
#         form = ReservaForm(instance=reserva)
#     return render(request, "reservasForm.html", {"method": request.method, "form": form, })


# ------ LISTAS DE PRECIO ------


def listasPrecio(request):
    listas = ListaPrecio.objects.all()
    context = {'listas': listas, }
    return render(request, 'listPrecios.html', context)


class ListaPrecioView(ListView):
    template_name = 'listPrecios.html'
    model = ListaPrecio
    paginate_by = 10
    context_object_name = 'listas'


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
            updated_lista = t_form.save(commit=False)
            updated_lista.save()

            i_formset = ListaPrecioDetalleInlineFormset(request.POST, instance=updated_lista)

            if i_formset.is_valid():
                i_formset.save()

                if lista is None:
                    messages.success(request, "La lista de precio fue creada.".format(updated_lista))
                else:
                    messages.success(request, "La lista de precio fue modificada.".format(updated_lista))
                return redirect("/listasprecio/edit/" + str(updated_lista.pk), listaPrecio_edit)
    else:
        t_form = ListaPrecioForm(instance=lista)
        i_formset = ListaPrecioDetalleInlineFormset(instance=lista)
        i_formset.extra = 4 if i_formset.queryset.count() < 1 else 1

    return render(request, "preciosform.html", {"method": request.method, "t_form": t_form, 'i_formset': i_formset})



# def ListaPrecioCreateView(request):
#     template_name = 'preciosform.html'
#     if request.method == 'GET':
#         t_form = ListaPrecioForm(request.GET or None)
#         i_formset = ListaPrecioDetalleInlineFormset(queryset=ListaPrecio.objects.none())
#     elif request.method == 'POST':
#         t_form = ListaPrecioForm(request.POST)
#         if t_form.is_valid():
#             t = t_form.save(commit=False)
#             t.save()
#
#             i_formset = ListaPrecioDetalleInlineFormset(request.POST, instance=t)
#             if i_formset.is_valid():
#                 i_formset.save()
#
#                 return redirect('/listasprecio/viewdetail/', pk=t.pk)
#
#     return render(request, template_name, {
#         't_form': t_form,
#         'i_formset': i_formset,
#     })


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


# ------ CAJA ------

# def movimientosCaja(request):
#     cajaMov = MovimientoCaja.objects.all()
#     context = {'cajaMov': cajaMov, }
#     return render(request, 'listCaja.html', context)


class MovimientosCajaView(ListView):
    template_name = 'listCaja.html'
    model = MovimientoCaja
    paginate_by = 15
    context_object_name = 'cajaMov'


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


#Reportes PDF

class ReporteReservasPDF(View):

    def cabecera(self, pdf):
        archivo_imagen = os.path.join(settings.BASE_DIR, '/HotelAguero/Hotel/static/Hotel/logo-ha-rep.jpg')
        pdf.drawImage(archivo_imagen, 40, 750, 120, 90, preserveAspectRatio=True)
        pdf.setFont("Helvetica", 16)
        pdf.drawString(230, 790, u"HOTEL AGÜERO")
        pdf.setFont("Helvetica", 14)
        pdf.drawString(200, 770, u"REPORTE DE RESERVAS")

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/pdf')
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)

        self.cabecera(pdf)
        y = 600
        self.tabla(pdf, y)

        pdf.showPage()
        pdf.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

    def tabla(self, pdf, y):
        encabezados = ('Cliente', 'Habitacion', 'Fecha de ingreso', 'Precio total')
        detalles = [(reserva.idCliente, reserva.idHabitacion, reserva.fechaIngreso, reserva.precioTotal) for reserva in
                    Reserva.objects.all()]

        detalle_orden = Table([encabezados] + detalles, colWidths=[2 * cm, 5 * cm, 5 * cm, 5 * cm])
        detalle_orden.setStyle(TableStyle(
            [
                ('ALIGN', (0, 0), (3, 0), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
            ]
        ))
        detalle_orden.wrapOn(pdf, 800, 600)
        detalle_orden.drawOn(pdf, 60, y)


#------SOLICITUDES------


def get_price(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        fecha_ingreso = data.get('fechaIngreso')
        fecha_egreso = data.get('fechaEgreso')
        personas = data.get('cantidadPersonas')
        lista_precio = ListaPrecio.objects.filter(vigenciaDesde__lte=fecha_ingreso, vigenciaHasta__gte=fecha_egreso).first()
        if lista_precio:

            detalle_precio = DetalleListaPrecio.objects.filter(idListaPrecio=lista_precio, cantidadPersonas=personas).first()

            if detalle_precio:
                print(detalle_precio)
                return JsonResponse({'precio':detalle_precio.precioPorDia})
        return JsonResponse({'precio': None})

