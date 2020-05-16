from rest_framework import serializers
from backend_crawler import models

class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Curso
        fields = ['periodo', 'id_eminus', 'nombre', 'nrc']
