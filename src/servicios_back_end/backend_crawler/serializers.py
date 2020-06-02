from rest_framework import serializers
from backend_crawler import models

class CursoSerializer(serializers.Serializer):
    periodo = serializers.CharField(max_length=100)
    id_eminus = serializers.CharField(max_length=100)
    nombre = serializers.CharField(max_length=100)

class Trabajos_terminadosSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Trabajos_terminados
        fields = ['usuario', 'periodo', 'nombre']
