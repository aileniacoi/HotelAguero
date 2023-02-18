from django import forms
from django_select2.forms import Select2Widget, ModelSelect2Widget
from django_select2 import forms as s2forms
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


class FiltrosReservaForm(forms.Form):
    fechaDesde = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    fechaHasta = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    mostrarHistoricas = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    soloGestionPendiente = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))


class ClienteWidget(s2forms.ModelSelect2Widget):
    model=Cliente
    search_fields = [
        "nombreYApellido__icontains",
        "dni__icontains",
    ]


class ReservaForm(forms.ModelForm):
    idCliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all(),
        widget=ModelSelect2Widget(
            data_url='/admin/Hotel/cliente/autocomplete/',
            data_view='select2_autoresponder',
            data_view_kwargs={'field_id': 'idCliente'},
            model=Cliente,
            search_fields=['nombreYApellido__icontains'],
            attrs={'class': 'form-control'}
        )
    )

    # idCliente = s2forms.ModelSelect2Widget(
    #     model=Cliente,
    #     search_fields=['nombreYApellido__icontains'],
    #     data_view='select2_autoresponder',
    #     data_view_kwargs={'field_id': 'idCliente'}
    # )

    class Meta:
        model = Reserva
        fields = "__all__"
        #exclude = ['idCliente', ]
        widgets = {
            'fechaRegistro': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fechaIngreso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fechaEgreso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cantidadPersonas': forms.TextInput(attrs={'class': 'form-control'}),
            'idHabitacion': forms.Select(attrs={'class': 'form-control'}),
            #'idCliente': ClienteWidget(attrs={'class': 'form-control'}),
            'seniaSolicitada': forms.NumberInput(attrs={'class': 'form-control'}),
            'precioTotal': forms.NumberInput(attrs={'class': 'form-control'}),
            'precioPorDia': forms.NumberInput(attrs={'class': 'form-control'}),
            'incluyeDesayuno': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fechaRegistro'].initial = datetime.now().date()
        self.fields['incluyeDesayuno'].initial = True


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


class FiltrosCajaForm(forms.Form):
    fechaDesde = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    fechaHasta = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    ingresos = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    egresos = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

PagosReservaInlineFormset = forms.inlineformset_factory(
    Reserva,
    MovimientoCaja,
    form=CajaForm,
    extra=0
)


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
