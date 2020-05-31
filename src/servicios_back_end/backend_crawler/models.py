from django.db import models

class Trabajos_terminados(models.Model):
    bitacora = models.CharField(null=False, blank=False, max_length=50)
    idEminus = models.CharField(null=False, blank=False, max_length=100)
    usuario = models.CharField(null=False, blank=False, max_length=20)
    periodo = models.CharField(null=False, blank=False, max_length=100)
    nombre = models.CharField(null=False, blank=False, max_length=100)
