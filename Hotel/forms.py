from django import forms
from .models import Cliente, Reserva, Habitacion


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = "__all__"
        widgets = {
            'nombreYApellido': forms.TextInput(attrs={'class': 'form-control'}),
            'dni': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = "__all__"
        widgets = {
            'fechaIngreso' : forms.TextInput(attrs={'class': 'form-control'}),
            'fechaEgreso' : forms.TextInput(attrs={'class': 'form-control'}),
            'cantidadPersonas' : forms.TextInput(attrs={'class': 'form-control'}),
            'idHabitacion' : forms.TextInput(attrs={'class': 'form-control'}),
            'idCliente' : forms.TextInput(attrs={'class': 'form-control'}),
            'senia' : forms.TextInput(attrs={'class': 'form-control'}),
            'precioTotal' : forms.TextInput(attrs={'class': 'form-control'}),
            'precioPorDia' : forms.TextInput(attrs={'class': 'form-control'}),
            'incluyeDesayuno' : forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones' : forms.TextInput(attrs={'class': 'form-control'}),
        }
