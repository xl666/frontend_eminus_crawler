from django.db import models

class Curso(models.Model):
    periodo = models.CharField(max_length=100)
    id_eminus = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    nrc = models.CharField(max_length=10)
