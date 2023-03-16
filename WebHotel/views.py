from django.shortcuts import render
from django.urls import reverse

# Create your views here.

def inicio2(request):
    return render(request, 'base2.html')

def index2(request):
    return render(request, 'index2.html')

def Conocenos(request):
    return render(request, 'ConocenosPage.html')

def Galeria(request):
    return render(request, 'GaleriaPage.html')

def Contacto(request):
    return render(request, 'ContactoPage.html')