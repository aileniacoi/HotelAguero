from django.shortcuts import render
from django.http import HttpResponse
from .models import Habitacion, Cliente, Reserva, ListaPrecio, MovimientoCaja, DetalleListaPrecio
from django.views.decorators.csrf import csrf_exempt

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from .forms import ClienteForm, HabitacionForm, ReservaForm, CajaForm, ListaPrecioForm, DetalleListaPrecioForm, \
    ListaPrecioDetalleInlineFormset, FiltrosCajaForm, FiltrosReservaForm, CancelacionReservaForm
from .serializers import ReservaSerializer, HabitacionSerializer, ClienteSerializer

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
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
import os
import json
from django.http import JsonResponse
from django.core import serializers
from django.utils import timezone

from datetime import datetime, date, time, timedelta
import calendar

from django.core.cache import cache
import requests

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

    pagos = MovimientoCaja.objects.filter(idReserva__isnull=False)

    for ingreso in ingresos:
        pagosReserva = pagos.filter(idReserva=ingreso)
        suma_pagos = pagosReserva.aggregate(valor_total=Sum('monto'))
        if suma_pagos['valor_total']:
            suma_pagos = suma_pagos['valor_total']
        else:
            suma_pagos = 0

        ingreso.saldo= ingreso.precioTotal - suma_pagos
        ingreso.reserva_sin_senia = suma_pagos == 0

    for egreso in egresos:
        pagosReserva = pagos.filter(idReserva=egreso)
        suma_pagos = pagosReserva.aggregate(valor_total=Sum('monto'))
        if suma_pagos['valor_total']:
            suma_pagos = suma_pagos['valor_total']
        else:
            suma_pagos = 0

        egreso.saldo= egreso.precioTotal - suma_pagos


    cantidadHabitaciones = Habitacion.objects.count()

    reservasActuales = Reserva.objects.filter(Q(fechaIngreso__lt=hoy) & Q(fechaEgreso__gt=hoy)).exclude(idHabitacion__isnull=True)

    for reserva in reservasActuales:
        pagosReserva = pagos.filter(idReserva=reserva)
        suma_pagos = pagosReserva.aggregate(valor_total=Sum('monto'))
        if suma_pagos['valor_total']:
            suma_pagos = suma_pagos['valor_total']
        else:
            suma_pagos = 0

        reserva.saldo= reserva.precioTotal - suma_pagos

    habitaciones_ocupadas = reservasActuales.values_list('idHabitacion', flat=True)
    if habitaciones_ocupadas.exists():
        habitaciones_disponibles = Habitacion.objects.exclude(pk__in=habitaciones_ocupadas).order_by('numero')
    else:
        habitaciones_disponibles = Habitacion.objects.all().order_by('numero')


    lista_precio = ListaPrecio.objects.filter(Q(vigenciaDesde__lte=hoy) & Q(vigenciaHasta__gte=hoy))[0]
    detalle_precios = DetalleListaPrecio.objects.filter(idListaPrecio=lista_precio)

    context = {'ingresos': ingresos, 'egresos': egresos, 'cantidadHabitaciones':cantidadHabitaciones,
               'habitacionesDisponibles': habitaciones_disponibles, 'reservasActuales': reservasActuales,
               'detallePrecios': detalle_precios}

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
    ordering = ['numero']


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
                                                       Q(fechaEgreso__range=[fecha_ingreso, fecha_egreso]))\
            .values_list('idHabitacion', flat=True)

        if habitaciones_ocupadas.exists():
            habitaciones_disponibles = Habitacion.objects.exclude(pk__in=habitaciones_ocupadas)
        else:
            habitaciones_disponibles = Habitacion.objects.all()

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


def cliente_edit_reserva(request, pk):
    if pk is not None:
        cliente = get_object_or_404(Cliente, pk=pk)
    else:
        cliente = None
    if request.method == "POST":
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            updated_cliente = form.save()
            return JsonResponse(ClienteSerializer(updated_cliente).data, safe=False)
    else:
        form = ClienteForm(instance=cliente)
        form.fields['nombreYApellido'].widget.attrs['readonly'] = 'readonly'
        form.fields['nombreYApellido'].widget.attrs['class'] = 'form-control-plaintext'
        form.fields['dni'].widget.attrs['readonly'] = 'readonly'
        form.fields['dni'].widget.attrs['class'] = 'form-control-plaintext'
    return render(request, "clienteresForm.html", {"method": request.method, "form_existente": form, "id_cliente": pk })


# ------ RESERVAS ------

# def reservas(request):
#     reservas = Reserva.objects.all()
#     context = {'reservas': reservas, }
#     return render(request, 'listReservas.html', context)

class ReservasView(ListView):
    template_name = 'listReservas.html'
    model = Reserva
    paginate_by = 15
    context_object_name = 'reservas'

    def get_queryset(self):
        form = FiltrosReservaForm(self.request.GET or None)
        queryset = super().get_queryset()
        now = timezone.now().date()
        if form.is_valid():
            fecha_desde = form.cleaned_data['fechaDesde']
            fecha_hasta = form.cleaned_data['fechaHasta']
            mostrar_historicas = form.cleaned_data['mostrarHistoricas']
            solo_gestion_pendiente = form.cleaned_data['soloGestionPendiente']

            if fecha_desde and fecha_hasta:
                queryset = queryset.filter(Q(fechaIngreso__range=(fecha_desde, fecha_hasta))|
                                           Q(fechaEngreso__range=(fecha_desde, fecha_hasta)))
            elif fecha_desde:
                queryset = queryset.filter(fechaIngreso__gte=fecha_desde)
            elif fecha_hasta:
                queryset = queryset.filter(fechaEgreso__lte=fecha_hasta)
            if not mostrar_historicas:
                queryset = queryset.exclude(fechaEgreso__lte=now)
                queryset = queryset.exclude(fechaCancelacion__isnull=False)
            if solo_gestion_pendiente:
                pagos_reservas = MovimientoCaja.objects.filter(idReserva__isnull=False).values_list('idReserva', flat=True).distinct()
                reservasVencidas = Reserva.objects.filter(fechaRegistro__lte=now-timedelta(days=2))\
                    .exclude(pk__in=pagos_reservas).values_list('pk', flat=True).distinct()

                queryset = queryset.filter(Q(idHabitacion__isnull=True) | Q(pk__in=reservasVencidas))
        else:
            queryset = queryset.exclude(fechaEgreso__lte=now)
            queryset = queryset.exclude(fechaCancelacion__isnull=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['form'] = FiltrosReservaForm(self.request.GET or None)

        now = timezone.now().date()

        pagos = MovimientoCaja.objects.filter(idReserva__in=context['reservas'].values_list('pk', flat=True))

        for reserva in context['reservas']:
            pagosReserva = pagos.filter(idReserva=reserva.pk)

            suma_pagos = pagosReserva.aggregate(valor_total=Sum('monto'))
            if suma_pagos['valor_total']:
                suma_pagos = suma_pagos['valor_total']
            else:
                suma_pagos = 0

            reserva_vencida = False
            if reserva.fechaRegistro + timedelta(days=2) < now and not pagosReserva.exists():
                reserva_vencida = True

            reserva.reserva_vencida = reserva_vencida
            reserva.saldo = reserva.precioTotal - suma_pagos

        return context


def reservasCalendario(request, mes=None, anio=None):

    feriados = get_holidays(anio)
    rangoFecha = calendar.monthrange(anio,mes)
    cantidadDias = rangoFecha[1]


    habitaciones = Habitacion.objects.all().order_by('numero')
    reservasQuery = Reserva.objects.filter(Q(fechaIngreso__month=mes, fechaIngreso__year=anio) |
                                           Q(fechaEgreso__month=mes, fechaEgreso__year=anio))\
        .exclude(fechaCancelacion__isnull=False)
    reservas = ReservaSerializer(reservasQuery, many=True)

    context = {'reservas': json.dumps(reservas.data), 'habitaciones': habitaciones,
               'cantidadDias': range(1, cantidadDias + 1), 'mes': mes, 'anio': anio, 'feriados': json.dumps(feriados)}
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

    pagosRealizados = pagos.filter(idTipoMovimiento='IN').aggregate(valor_total=Sum('monto'))

    if pagosRealizados['valor_total']:
        pagosRealizados = pagosRealizados['valor_total']
    else:
        pagosRealizados = 0

    if request.method == 'POST':
        form_reserva = ReservaForm(request.POST, instance=reserva)
        form_cliente = ClienteForm(request.POST, instance=cliente)
        #p_formset = PagosReservaInlineFormset(instance=reserva)

        saldo = reserva.precioTotal - pagosRealizados

        if form_reserva.is_valid() and form_cliente.is_valid():
            form_reserva.save()
            form_cliente.save()
            return redirect("reservaEdit", pk=reserva.pk)

    else:
        form_reserva = ReservaForm(instance=reserva)
        form_cliente = ClienteForm(instance=cliente)
        #p_formset = PagosReservaInlineFormset(instance=reserva)

        print(form_reserva)

        saldo = reserva.precioTotal - pagosRealizados
    return render(request, 'reservaDetail.html', {'form_reserva': form_reserva, 'form_cliente': form_cliente, 'pagos': pagos,
                                                  'saldo': saldo, 'id_reserva': pk})


def alta_reserva(request):
    reserva = None
    cliente = None
    if request.method == 'POST':
        form_reserva = ReservaForm(request.POST, instance=reserva)
        form_cliente = ClienteForm(request.POST, instance=cliente)

        if form_reserva.is_valid():
            reserva = form_reserva.save(commit=False)
            print(form_reserva)
            if bool(request.POST['idCliente']):
                form_reserva.save()

            else:
                if form_cliente.is_valid():
                    cliente = form_cliente.save()
                    reserva.idCliente = cliente
                    form_reserva.save()

            messages.success(request, "La reserva \"{}\" fue creada.".format(reserva))

            return redirect("reservaEdit", pk=reserva.pk)
        else:
            print(form_reserva.errors)


    else:
        form_reserva = ReservaForm(instance=reserva)
        form_cliente = ClienteForm(instance=cliente)
    return render(request, 'nuevareserva.html', {'form_reserva': form_reserva, 'form_cliente': form_cliente})


def cancelar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if request.method == 'POST':
        reserva.fechaCancelacion = request.POST['fecha']

        reserva.save()

        montoDevuelto = int(request.POST['montoDevuelto'])

        if montoDevuelto > 0:
            devolucion = MovimientoCaja(idReserva=reserva,
                                        fecha=request.POST['fecha'],
                                        idTipoMovimiento='EG',
                                        idConcepto='DEV',
                                        monto=montoDevuelto,
                                        idFormaPago='TRA')
            devolucion.save()

        return JsonResponse({'success': True})

    else:
        form_cancel = CancelacionReservaForm(initial={'idReserva': reserva.pk})
        return render(request, 'cancelreserva.html', {'form_cancel': form_cancel, 'reserva': reserva})



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


class ListaPrecioBajaView(SuccessMessageMixin, DeleteView):
    model = ListaPrecio
    template_name = 'listapreciobaja.html'
    success_url = '/listasprecio'
    success_message = 'La lista de precios fue eliminada.'


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

    def get_queryset(self):
        form = FiltrosCajaForm(self.request.GET or None)
        queryset = super().get_queryset()
        if form.is_valid():
            fecha_desde = form.cleaned_data['fechaDesde']
            fecha_hasta = form.cleaned_data['fechaHasta']
            ingresos = form.cleaned_data['ingresos']
            egresos = form.cleaned_data['egresos']
            if fecha_desde and fecha_hasta:
                queryset = queryset.filter(fecha__range=(fecha_desde, fecha_hasta))
            elif fecha_desde:
                queryset = queryset.filter(fecha__gte=fecha_desde)
            elif fecha_hasta:
                queryset = queryset.filter(fecha__lte=fecha_hasta)
            if not ingresos:
                queryset = queryset.exclude(idTipoMovimiento="IN")
            if not egresos:
                queryset = queryset.exclude(idTipoMovimiento="EG")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FiltrosCajaForm(self.request.GET or None)
        return context

@csrf_exempt
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


class CajaBajaView(SuccessMessageMixin, DeleteView):
    model = MovimientoCaja
    template_name = 'cajabaja.html'
    success_url = '/movimientoscaja'
    success_message = 'El movimiento de caja fue eliminado.'


def agregar_pago_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, pk=reserva_id)

    if request.method == "POST":
        form = CajaForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = CajaForm(initial={'idReserva': reserva.pk, 'idTipoMovimiento': "IN"})
        form.fields['idConcepto'].choices = [(MovimientoCaja.SENIA, 'Seña'), (MovimientoCaja.SALDO, 'Saldo')]
        return render(request, 'agregarpago.html', {'form_pago': form, 'id_reserva': reserva_id})




#Reportes PDF

class ReporteReservasPDF(View):

    def cabecera(self, pdf):
        archivo_imagen = os.path.join(settings.BASE_DIR, '/HotelAguero/Hotel/static/Hotel/logo-ha-rep.jpg')
        pdf.drawImage(archivo_imagen, 40, 740, 120, 90, preserveAspectRatio=True)
        pdf.setFont("Helvetica", 16)
        pdf.drawString(230, 790, u"HOTEL AGÜERO")
        pdf.setFont("Helvetica", 14)
        pdf.drawString(200, 770, u"REPORTE DE RESERVAS")

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/pdf')
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)

        self.cabecera(pdf)
        y = 680
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


def ReporteReservasCalendarioPDF(request, mes, anio):

    response = HttpResponse(content_type='application/pdf')
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, landscape(A4))

    archivo_imagen = os.path.join(settings.BASE_DIR, '/HotelAguero/Hotel/static/Hotel/logo-ha-rep.jpg')
    pdf.drawImage(archivo_imagen, 100, 490, 120, 90, preserveAspectRatio=True)
    pdf.setFont("Helvetica", 16)
    pdf.drawString(350, 540, u"HOTEL AGÜERO")
    pdf.setFont("Helvetica", 14)
    pdf.drawString(330, 510, u"REPORTE DE RESERVAS")

    y = 200

    rangoFecha = calendar.monthrange(anio, mes)
    cantidadDias = rangoFecha[1]

    habitaciones = Habitacion.objects.all().order_by('numero')
    reservas = Reserva.objects.filter(Q(fechaIngreso__month=mes, fechaIngreso__year=anio) |
                                      Q(fechaEgreso__month=mes, fechaEgreso__year=anio))

    estado_reserva = {hab.numero: [False for i in range(cantidadDias)] for hab in habitaciones}

    for res in reservas:
        habitacion = res.idHabitacion.numero
        ingreso = res.fechaIngreso.day
        egreso = res.fechaEgreso.day
        for i in range(ingreso - 1, egreso):
            estado_reserva[habitacion][i] = True

    datosTabla = [[''] + [(dia + 1) for dia in range(cantidadDias)]]

    for hab in habitaciones:
        row = [hab.numero] + ['' if not estado_reserva[hab.numero][i] else 'X' for i in range(cantidadDias)]
        datosTabla.append(row)

    detalle_orden = Table(datosTabla, colWidths=[0.9 * cm])
    detalle_orden.setStyle(TableStyle(
        [
            ('ALIGN', (0, 0), (3, 0), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]
    ))
    detalle_orden.wrapOn(pdf, 800, 400)
    detalle_orden.drawOn(pdf, 20, y)

    pdf.showPage()
    pdf.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def ReporteCajaPDF(request):

    fecha_desde = request.GET.get('fechaDesde')
    fecha_hasta = request.GET.get('fechaHasta')
    ingresos = request.GET.get('ingresos')
    egresos = request.GET.get('egresos')

    response = HttpResponse(content_type='application/pdf')

    movimientos = MovimientoCaja.objects.all()

    if fecha_desde != '':
        movimientos = movimientos.filter(fecha__gte=fecha_desde)
    if fecha_hasta != '':
        movimientos = movimientos.filter(fecha__lte=fecha_hasta)

    if ingresos != 'true':
        movimientos = movimientos.exclude(idTipoMovimiento='IN')
    if egresos != 'true':
        movimientos = movimientos.exclude(idTipoMovimiento='EG')

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    #Cabecera
    archivo_imagen = os.path.join(settings.BASE_DIR, '/HotelAguero/Hotel/static/Hotel/logo-ha-rep.jpg')
    pdf.drawImage(archivo_imagen, 40, 740, 120, 90, preserveAspectRatio=True)
    pdf.setFont("Helvetica", 16)
    pdf.drawString(230, 790, u"HOTEL AGÜERO")
    pdf.setFont("Helvetica", 14)
    pdf.drawString(228, 770, u"REPORTE DE CAJA")

    y = 650

    #tabla
    encabezados = ('Fecha', 'Tipo', 'Concepto', 'Monto', 'N° Reserva')
    detalles = [(mov.fecha.strftime("%d/%m/%Y"), mov.get_idTipoMovimiento_display(), mov.get_idConcepto_display(),'$ ' + str(mov.monto),
                 mov.idReserva) for mov in movimientos]

    detalle_orden = Table([encabezados] + detalles, colWidths=[3 * cm, 3 * cm, 3.5 * cm, 3.5 * cm, 5 *cm])
    detalle_orden.setStyle(TableStyle(
        [
            ('ALIGN', (0, 0), (3, 0), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]
    ))
    detalle_orden.wrapOn(pdf, 800, 600)
    detalle_orden.drawOn(pdf, 60, y)


    pdf.showPage()
    pdf.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    response['Content-Disposition'] = 'attachment; filename="movimientos.pdf"'
    return response

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


def BuscarReservaCliente(request):
    if request.method == "POST":
        cliente_buscado = request.POST['cliente_buscado']
        clientes = Cliente.objects.filter(Q(nombreYApellido__contains=cliente_buscado) |
                                          Q(dni__contains=cliente_buscado))

        now = timezone.now().date()

        reservas = Reserva.objects.filter(idCliente__in=clientes).order_by('-fechaIngreso')
        pagos = MovimientoCaja.objects.filter(idReserva__in=reservas.values_list('pk', flat=True))

        for reserva in reservas:
            pagosReserva = pagos.filter(idReserva=reserva.pk)

            suma_pagos = pagosReserva.aggregate(valor_total=Sum('monto'))
            if suma_pagos['valor_total']:
                suma_pagos = suma_pagos['valor_total']
            else:
                suma_pagos = 0

            reserva_vencida = False
            if reserva.fechaRegistro + timedelta(days=2) < now and not pagosReserva.exists():
                reserva_vencida = True

            reserva.reserva_vencida = reserva_vencida
            reserva.saldo = reserva.precioTotal - suma_pagos

        return render(request, 'listReservas.html', {'cliente_buscado': cliente_buscado, 'reservas': reservas})
    else:
        return render(request, 'listReservas.html', {})


def get_holidays(year):
    cache_key = f"holidays_{year}"
    holidays = cache.get(cache_key)

    if holidays is not None:
        return holidays
    else:
        url = f"https://calendarific.com/api/v2/holidays?api_key=c19a938c72a4d126bb791e2f71fa75e329233903&country=AR&year={year}"
        response = requests.get(url)

        if response.status_code == 200:
            holidays = response.json()["response"]["holidays"]
            cache.set(cache_key, holidays)
            return holidays
        else:
            return None
