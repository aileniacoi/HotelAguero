# Generated by Django 4.1.6 on 2023-02-08 23:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Hotel', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reserva',
            name='cantidadPersonas',
            field=models.IntegerField(verbose_name='Personas'),
        ),
        migrations.AlterField(
            model_name='reserva',
            name='idHabitacion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Hotel.habitacion', verbose_name='Habitación'),
        ),
        migrations.AlterField(
            model_name='reserva',
            name='importeDescuento',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Importe de descuento'),
        ),
        migrations.AlterField(
            model_name='reserva',
            name='porcentajeDescuento',
            field=models.IntegerField(blank=True, null=True, verbose_name='Porcentaje de descuento'),
        ),
    ]
