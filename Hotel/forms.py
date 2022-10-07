from django import forms
from .models import Cliente, Reserva, Habitacion, MovimientoCaja, ListaPrecio


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
        widgets = {
            'fechaIngreso': forms.DateInput(attrs={'class': 'form-control'}),
            'fechaEgreso': forms.DateInput(attrs={'class': 'form-control'}),
            'cantidadPersonas': forms.TextInput(attrs={'class': 'form-control'}),
            'idHabitacion': forms.Select(attrs={'class': 'form-control'}),
            'idCliente': forms.Select(attrs={'class': 'form-control'}),
            'senia': forms.NumberInput(attrs={'class': 'form-control'}),
            'precioTotal': forms.NumberInput(attrs={'class': 'form-control'}),
            'precioPorDia': forms.NumberInput(attrs={'class': 'form-control'}),
            'incluyeDesayuno': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control'}),
        }


class CajaForm(forms.ModelForm):
    class Meta:
        model = MovimientoCaja
        fields = "__all__"
        widgets = {
            'idTipoMovimiento': forms.Select(attrs={'class': 'form-control'}),
            'idConcepto': forms.Select(attrs={'class': 'form-control'}),
            'idFormaPago': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
            'numeroComprobante': forms.TextInput(attrs={'class': 'form-control'}),
            'idReserva': forms.Select(attrs={'class': 'form-control'})
        }
