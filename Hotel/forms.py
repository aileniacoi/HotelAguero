from django import forms
from datetime import datetime
from .models import Cliente, Reserva, Habitacion, MovimientoCaja, ListaPrecio, DetalleListaPrecio


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
            'esPlantaBaja': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'habilitada': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = "__all__"
        exclude = ['idCliente', ]
        widgets = {
            'fechaRegistro': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fechaIngreso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fechaEgreso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cantidadPersonas': forms.TextInput(attrs={'class': 'form-control'}),
            'idHabitacion': forms.Select(attrs={'class': 'form-control'}),
            #'idCliente': forms.Select(attrs={'class': 'form-control'}),
            'seniaSolicitada': forms.NumberInput(attrs={'class': 'form-control'}),
            'precioTotal': forms.NumberInput(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'precioPorDia': forms.NumberInput(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'incluyeDesayuno': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fechaRegistro'].initial = datetime.now().date()
        self.fields['incluyeDesayuno'].initial = True

# class ReservaMultiForm(forms.Form):
#     cliente_form = ClienteForm()
#     reserva_form = ReservaForm()


class PagosFormset():
    class Meta:
        model = MovimientoCaja
        fields = '__all__'
        widgets = {
            'idConcepto': forms.Select(attrs={'class': 'form-control'}),
            'idFormaPago': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
        }


PagosReservaInlineFormset = forms.inlineformset_factory(
    Reserva,
    MovimientoCaja,
    form=PagosFormset,
    extra=1
)


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


class ListaPrecioForm(forms.ModelForm):
    class Meta:
        model = ListaPrecio
        fields = "__all__"
        widgets = {
            'idTipoLista': forms.Select(attrs={'class': 'form-control'}),
            'vigenciaDesde': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'vigenciaHasta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }


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
