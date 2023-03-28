from django import forms
from datetime import datetime
from .models import Cliente, Reserva, Habitacion, MovimientoCaja, ListaPrecio, DetalleListaPrecio
from django.db.models import Q, Sum


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = "__all__"
        widgets = {
            'nombreYApellido': forms.TextInput(attrs={'class': 'form-control'}),
            'dni': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
        }



class HabitacionForm(forms.ModelForm):
    class Meta:
        model = Habitacion
        fields = "__all__"
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'plazas': forms.TextInput(attrs={'class': 'form-control'}),
            'idEstado': forms.Select(attrs={'class': 'form-control'}),
            'esPlantaBaja': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['idEstado'].initial = "LIS"


class FiltrosReservaForm(forms.Form):
    fechaDesde = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    fechaHasta = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    mostrarHistoricas = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    soloGestionPendiente = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = "__all__"
        #exclude = ['idCliente', ]
        widgets = {
            #'pk': forms.NumberInput(),
            'fechaRegistro': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fechaIngreso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fechaEgreso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cantidadPersonas': forms.TextInput(attrs={'class': 'form-control'}),
            'idHabitacion': forms.Select(attrs={'class': 'form-control'}),
            'idCliente': forms.Select(attrs={'class': 'form-control select-search', 'style': 'width:350px;'}),
            'seniaSolicitada': forms.NumberInput(attrs={'class': 'form-control'}),
            'precioTotal': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'precioPorDia': forms.NumberInput(attrs={'class': 'form-control'}),
            'incluyeDesayuno': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'fechaCancelacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fechaRegistro'].initial = datetime.now().date()
        self.fields['incluyeDesayuno'].initial = True
        #self.fields['idCliente'].required = False

    def clean(self):
        cleaned_data = super().clean()
        fechaDesde = cleaned_data.get('fechaIngreso')
        fechaHasta = cleaned_data.get('fechaEgreso')

        if fechaDesde and fechaHasta:
            if fechaDesde > fechaHasta:
                raise forms.ValidationError('La fecha de ingreso no puede ser mayor a la de egreso')


class CancelacionReservaForm(forms.Form):
    idReserva = forms.IntegerField(widget=forms.HiddenInput)
    fecha = forms.DateField(required=True, label='Fecha', initial=datetime.now().date(), widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    montoDevuelto = forms.IntegerField(required=False, label='Monto devuelto', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    formaPago = forms.CharField(label='Forma de pago', widget=forms.Select(choices=[('', '-------')] + MovimientoCaja.FORMAPAGO, attrs={'class': 'form-control'}), required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        idReserva = self.initial.get('idReserva')
        self.fields['montoDevuelto'].initial = 0


class RegistroCheckInForm(forms.Form):
    idReserva = forms.IntegerField(widget=forms.HiddenInput)
    nombreCliente = forms.CharField(label='Cliente', widget=forms.TextInput(attrs={'class': 'form-control form-control-plaintext', 'readonly': 'readonly'}))
    dniCliente = forms.CharField(label='DNI', widget=forms.TextInput(attrs={'class': 'form-control form-control-plaintext', 'readonly': 'readonly'}))
    habitacion = forms.IntegerField(label='Habitación', widget=forms.TextInput(attrs={'class': 'form-control form-control-plaintext', 'readonly': 'readonly'}))
    cantidadPesonas = forms.IntegerField(label='Pax', widget=forms.TextInput(attrs={'class': 'form-control form-control-plaintext', 'readonly': 'readonly'}))
    saldo = forms.IntegerField(label='Saldo', widget=forms.TextInput(attrs={'class': 'form-control form-control-plaintext', 'readonly': 'readonly'}))
    pagoSaldo = forms.IntegerField(required=False, label='Pago', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    formaPago = forms.CharField(label='Forma de pago', widget=forms.Select(choices=[('', '-------')] + MovimientoCaja.FORMAPAGO, attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        idReserva = self.initial.get('idReserva')
        reserva = Reserva.objects.get(pk=idReserva)
        cliente = reserva.idCliente

        pagosReserva = MovimientoCaja.objects.filter(idReserva=reserva.pk)

        suma_pagos = pagosReserva.aggregate(valor_total=Sum('monto'))
        if suma_pagos['valor_total']:
            suma_pagos = suma_pagos['valor_total']
        else:
            suma_pagos = 0

        self.fields['nombreCliente'].initial = cliente.nombreYApellido
        self.fields['dniCliente'].initial = cliente.dni
        self.fields['habitacion'].initial = reserva.idHabitacion.numero
        self.fields['cantidadPesonas'].initial = reserva.cantidadPersonas
        self.fields['saldo'].initial = reserva.precioTotal - suma_pagos
        self.fields['pagoSaldo'].initial = 0


class RegistroCheckOutForm(forms.Form):
    idReserva = forms.IntegerField(widget=forms.HiddenInput)
    nombreCliente = forms.CharField(label='Cliente', widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    habitacion = forms.IntegerField(label='Habitación', widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    saldo = forms.IntegerField(label='Saldo', widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
    pagoSaldo = forms.IntegerField(required=False, label='Pago', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    formaPago = forms.CharField(label='Forma de pago', widget=forms.Select(choices=[('', '-------')] + MovimientoCaja.FORMAPAGO, attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        idReserva = self.initial.get('idReserva')
        reserva = Reserva.objects.get(pk=idReserva)
        cliente = reserva.idCliente

        pagosReserva = MovimientoCaja.objects.filter(idReserva=reserva.pk)

        suma_pagos = pagosReserva.aggregate(valor_total=Sum('monto'))
        if suma_pagos['valor_total']:
            suma_pagos = suma_pagos['valor_total']
        else:
            suma_pagos = 0

        saldo = reserva.precioTotal - suma_pagos

        if saldo > 0:
            self.fields['saldo'].initial = saldo
            self.fields['pagoSaldo'].initial = 0

        self.fields['nombreCliente'].initial = cliente.nombreYApellido
        self.fields['habitacion'].initial = reserva.idHabitacion.numero



class CajaForm(forms.ModelForm):
    class Meta:
        model = MovimientoCaja
        fields = "__all__"
        widgets = {
            'idTipoMovimiento': forms.Select(attrs={'class': 'form-control'}),
            'idConcepto': forms.Select(attrs={'class': 'form-control'}),
            'idFormaPago': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
            'numeroComprobante': forms.TextInput(attrs={'class': 'form-control'}),
            'idReserva': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha'].initial = datetime.now().date()


class FiltrosCajaForm(forms.Form):
    fechaDesde = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    fechaHasta = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    ingresos = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    egresos = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

# PagosReservaInlineFormset = forms.inlineformset_factory(
#     Reserva,
#     MovimientoCaja,
#     form=CajaForm,
#     extra=0
# )

class FiltrosListaPrecio(forms.Form):
    fechaDesde = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    fechaHasta = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    tipoLista = forms.CharField(widget=forms.Select(choices=[('', '-------')] + ListaPrecio.TIPOLISTA, attrs={'class': 'form-control'}), required=False)
    mostrarHistoricas = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))


class ListaPrecioForm(forms.ModelForm):
    class Meta:
        model = ListaPrecio
        fields = "__all__"
        widgets = {
            'idTipoLista': forms.Select(attrs={'class': 'form-control'}),
            'vigenciaDesde': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'vigenciaHasta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }

    def clean(self):
        cleaned_data = super().clean()
        vigenciaDesde = cleaned_data.get('vigenciaDesde')
        vigenciaHasta = cleaned_data.get('vigenciaHasta')

        if vigenciaDesde and vigenciaHasta:
            # Verificamos si ya existe una lista de precios para las fechas seleccionadas

            if vigenciaDesde > vigenciaHasta:
                raise forms.ValidationError('La fecha de inicio de vigencia debe ser menor a la de finalización')

            listasExistentes = ListaPrecio.objects.filter(
                Q(vigenciaDesde__range=(vigenciaDesde, vigenciaHasta)) |
                Q(vigenciaHasta__range=(vigenciaDesde, vigenciaHasta))
            ).exclude(pk=self.instance.pk)

            if listasExistentes.exists():

                datosLista = ''

                for lista in listasExistentes:
                    datosLista += f'<li>{lista.get_idTipoLista_display()} (desde: {lista.vigenciaDesde.strftime("%d/%m/%Y")}, ' \
                                  f'hasta: {lista.vigenciaHasta.strftime("%d/%m/%Y")})</li>'

                raise forms.ValidationError(f'Las fechas seleccionadas se superponen con otra lista de precios: <br> <ul>{datosLista}</ul>')


class DetalleListaPrecioForm(forms.ModelForm):
    class Meta:
        model = DetalleListaPrecio
        fields = '__all__'
        widgets = {
            'cantidadPersonas': forms.NumberInput(attrs={'class': 'form-control'}),
            'precioPorDia': forms.NumberInput(attrs={'class': 'form-control'})
        }


ListaPrecioDetalleInlineFormset = forms.inlineformset_factory(
    ListaPrecio,
    DetalleListaPrecio,
    form=DetalleListaPrecioForm,
    extra=4
)
