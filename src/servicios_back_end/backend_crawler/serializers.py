from rest_framework import serializers
from backend_crawler import models

class CursoSerializer(serializers.Serializer):
    periodo = serializers.CharField(max_length=100)
    id_eminus = serializers.CharField(max_length=100)
    nombre = serializers.CharField(max_length=100)
