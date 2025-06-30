from rest_framework import serializers
from apps.modelos.models import CargaSiatf,PlazosDetalle

class PlazosDetalladoCrearSerializer(serializers.Serializer):
    file = serializers.FileField()
    dependencia = serializers.CharField()

class PlazosCrearSerializer(serializers.Serializer):
    file = serializers.FileField()
    dependencia = serializers.CharField()

class CargaCrearSerializer(serializers.Serializer):
    file = serializers.FileField()
    dependencia = serializers.CharField()
    mes = serializers.IntegerField(min_value=1, max_value=12)
    anio = serializers.IntegerField(min_value=2000, max_value=2100)

class CargaTotalSerializer(serializers.Serializer):
    file = serializers.FileField()
    dependencia = serializers.CharField()

class CargaSiatfSerializer(serializers.Serializer):
    file = serializers.FileField()
    dependencia = serializers.CharField()
class CargaAnioCrearSerializer(serializers.Serializer):
    file = serializers.FileField()
    dependencia = serializers.CharField()
    anio = serializers.IntegerField()






