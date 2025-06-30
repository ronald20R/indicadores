from typing import Any
from django.contrib.auth.models import AbstractUser
from django.db import models



class PlazosDetalle(models.Model):
    dependencia = models.CharField(max_length=256)
    nombre_fiscal =models.CharField(max_length=256)
    etapa =models.CharField(max_length=256)
    estado = models.CharField(max_length=256)
    dentro_plazo = models.IntegerField(default=0)
    por_vencer = models.IntegerField(default=0)
    vencidos = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre_fiscal



class Plazos(models.Model):
    dentro_plazo = models.IntegerField(default=0)
    por_vencer = models.IntegerField(default=0)
    vencidos = models.IntegerField(default=0)
    dependencia = models.CharField(max_length=256)
    nombre_fiscal = models.CharField(max_length=256)
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_modificacion = models.DateField(auto_now=True)
    tipo_caso = models.CharField(max_length=256)
    # tipo_caso = models.ForeignKey(TipoCaso, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_fiscal

class Carga(models.Model):
    nombre_fiscal = models.CharField(max_length=256)
    casos_resueltos = models.IntegerField(default=0)
    casos_ingresados =  models.IntegerField(default=0)
    casos_en_tramite =  models.IntegerField(default=0)
    dependencia = models.CharField(max_length=256)
    fecha = models.DateField(blank=False)
    sentencias = models.IntegerField(default=0)
    archivos_consentidos = models.IntegerField(default=0)
    archivo_califica = models.IntegerField(default=0)
    archivo_preliminar = models.IntegerField(default=0)
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_modificacion = models.DateField(auto_now=True)

    def __str__(self):
        return self.nombre_fiscal

class CargaTotal(models.Model):
    nombre_fiscal = models.CharField(max_length=256)
    total_tramite =  models.IntegerField(default=0)
    tramite_historico = models.IntegerField(default=0)
    asignados = models.IntegerField(default=0)
    pendientes =  models.IntegerField(default=0)
    calificados =  models.IntegerField(default=0)
    dependencia = models.CharField(max_length=256)
    preliminares = models.IntegerField(default=0)
    investigacion_pnp = models.IntegerField(default=0)
    investigacion_preparatoria = models.IntegerField(default=0)
    etapa_intermedia = models.IntegerField(default=0)
    etapa_juzgamiento = models.IntegerField(default=0)
    fecha_modificacion = models.DateField(auto_now=True)

    def __str__(self):
        return self.dependencia

class Usuario(AbstractUser):
    def __str__(self):
        return self.username
    class Meta:
        ordering = ('id',)

class MateriaDelito(models.Model):
    materia = models.CharField(max_length=256)
    cantidad = models.IntegerField(default=0)
    mes = models.CharField(max_length=256)
    dependencia =  models.CharField(max_length=256)

    def __str__(self):
        return self.materia


class TramitesMensual(models.Model):
    dependencia = models.CharField(max_length=256)
    nombre_fiscal = models.CharField(max_length=256)
    # fecha_ingreso = models.DateField(blank=False)
    # fecha_conclusion = models.DateField(blank=True, null= True)
    mes = models.CharField(max_length=256)
    total_tramite = models.IntegerField(default=0)
    tramite_mes = models.IntegerField(default=0)
    resuelto_mes = models.IntegerField(default=0)
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_modificacion = models.DateField(auto_now=True)

    def __str__(self):
        return self.dependencia

class CargaSiatf(models.Model):
    dependencia = models.CharField(max_length=256)
    estado = models.CharField(max_length=256)
    especialidad = models.CharField(max_length=256)
    casos_ingresados = models.IntegerField(default=0)
    cantidad  =models.IntegerField(default=0)
    

    def __str__(self):
        return self.dependencia
    

class CargaAnio(models.Model):
    dependencia = models.CharField(max_length=256)
    nombre_fiscal =models.CharField(max_length=256)
    resueltos = models.IntegerField(default=0)
    tramites = models.IntegerField(default=0)
    ingresados = models.IntegerField(default=0)
    anio = models.IntegerField(verbose_name="Año")
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_modificacion = models.DateField(auto_now=True)

    def __str__(self):  
        return self.dependencia + " " + str(self.anio)
    