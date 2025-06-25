import os
import shutil

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db import transaction
from rest_framework.permissions import DjangoModelPermissions

from apps.api.functions import (
    procesar_archivo_plazos,
    procesar_carga_total,
    procesar_carga_laboral,
    procesar_carga_siatf,
    procesar_archivo_plazos_detallado   
)
from apps.modelos.models import Plazos


def extraer_dependencia_desde_nombre(nombre_archivo):
    base = os.path.splitext(nombre_archivo)[0]
    dependencia = base.split('_')[0]
    return dependencia

class ProcesarArchivosPlazosView(APIView):
    queryset = Plazos.objects.none()
    permission_classes = [DjangoModelPermissions]

    def post(self, request):
        mes = request.data.get('mes')
        anio = request.data.get('anio')

        if not mes or not anio:
            return Response({'error': 'Debe enviar mes y anio'}, status=status.HTTP_400_BAD_REQUEST)

        resultados = []

        #---------- PLAZOS DETALLADO---------
        carpeta_plazos_detallado = 'data/PlazosDetallado'
        carpeta_destino_plazos_detallado = 'dataprocesada/PlazosDetallado'
        os.makedirs(carpeta_destino_plazos_detallado, exist_ok=True)
        if os.path.exists(carpeta_plazos_detallado):
            archivos_plazos_detallado = [f for f in os.listdir(carpeta_plazos_detallado) if f.endswith('.csv')]
            for archivo in archivos_plazos_detallado:
                dependencia = extraer_dependencia_desde_nombre(archivo) 
                ruta_archivo = os.path.join(carpeta_plazos_detallado, archivo)
                try:
                    with open(ruta_archivo, 'rb') as f:
                        success, mensaje = procesar_archivo_plazos_detallado(f, dependencia)
                except Exception as e:
                    resultados.append({
                        'tipo': 'Plazos Detallado',
                        'dependencia': dependencia,
                        'error': str(e)
                    })
                if success:
                    shutil.move(ruta_archivo, os.path.join(carpeta_destino_plazos_detallado, archivo))  
                else:   
                    resultados.append({
                        'tipo': 'Plazos Detallado',
                        'dependencia': dependencia,
                        'error': mensaje
                    })

        # ---------- PLZAZOS ----------
        carpeta_plazos = 'data/Plazos'
        carpeta_destino_plazos = 'dataprocesada/Plazos'
        os.makedirs(carpeta_destino_plazos, exist_ok=True)

        if os.path.exists(carpeta_plazos):
            archivos_plazos = [f for f in os.listdir(carpeta_plazos) if f.endswith('.csv')]

            for archivo in archivos_plazos:
                dependencia = extraer_dependencia_desde_nombre(archivo)
                ruta_archivo = os.path.join(carpeta_plazos, archivo)

                try:
                    with open(ruta_archivo, 'rb') as f:
                        success, mensaje = procesar_archivo_plazos(f, dependencia)

                    if success:
                        shutil.move(ruta_archivo, os.path.join(carpeta_destino_plazos, archivo))

                    resultados.append({
                        'tipo': 'Plazos',
                        'dependencia': dependencia,
                        'mensaje': 'Archivo procesado correctamente'
                    })
                except Exception as e:
                    resultados.append({
                        'tipo': 'Plazos',
                        'dependencia': dependencia,
                        'error': str(e)
                    })

        # ---------- RESUMEN CARGA TOTAL ----------
        carpeta_carga = 'data/ResumenCarga'
        carpeta_destino_carga = 'dataprocesada/ResumenCarga'
        os.makedirs(carpeta_destino_carga, exist_ok=True)

        if os.path.exists(carpeta_carga):
            archivos_carga = [f for f in os.listdir(carpeta_carga) if f.endswith('.csv')]

            for archivo in archivos_carga:
                dependencia = extraer_dependencia_desde_nombre(archivo)
                ruta_archivo = os.path.join(carpeta_carga, archivo)

                try:
                    with open(ruta_archivo, 'rb') as f:
                        response_data, response_status = procesar_carga_total(f, dependencia)

                    if response_status == status.HTTP_201_CREATED:
                        shutil.move(ruta_archivo, os.path.join(carpeta_destino_carga, archivo))

                    # resultados.append({
                    #     'tipo': 'Plazos',
                    #     'dependencia': dependencia,
                    #     'mensaje': 'Archivo procesado correctamente'
                    # })
                except Exception as e:
                    resultados.append({
                        'tipo': 'Plazos',
                        'dependencia': dependencia,
                        'error': str(e)
                    })

        # ---------- CARGA LABORAL ----------
        carpeta_laboral = 'data/CargaTotal'
        carpeta_destino_laboral = 'dataprocesada/CargaTotal'
        os.makedirs(carpeta_destino_laboral, exist_ok=True)

        if os.path.exists(carpeta_laboral):
            archivos_laboral = [f for f in os.listdir(carpeta_laboral)]
            for archivo in archivos_laboral:
                dependencia = extraer_dependencia_desde_nombre(archivo)
                ruta_archivo = os.path.join(carpeta_laboral, archivo)

                try:
                    with open(ruta_archivo, 'rb') as f:
                        response_data, response_status = procesar_carga_laboral(f, dependencia, mes, anio)

                    if response_status==status.HTTP_201_CREATED:
                        shutil.move(ruta_archivo, os.path.join(carpeta_destino_laboral, archivo))
                        # resultados.append({
                        #     'tipo': 'Plazos',
                        #     'dependencia': dependencia,
                        #     'mensaje': 'Archivo procesado correctamente'
                        # })
                    else:
                        resultados.append({
                            'tipo': 'Plazos',
                            'dependencia': dependencia,
                            'error': response_data.get('detalle') or 'No se pudo procesar el archivo'
                        })
                except Exception as e:
                    resultados.append({
                        'tipo': 'Plazos',
                        'dependencia': dependencia,
                        'error': str(e)
                    })

        # ---------- CARGA SIATF ----------
        carpeta_siatf = 'data/CargaSiatf'
        carpeta_destino_siatf = 'dataprocesada/CargaSiatf'
        os.makedirs(carpeta_destino_siatf, exist_ok=True)
        
        if os.path.exists(carpeta_siatf):
            archivos_siatf = [f for f in os.listdir(carpeta_siatf) if f.endswith('.xlsx')]
            for archivo in archivos_siatf:
                dependencia = extraer_dependencia_desde_nombre(archivo)
                ruta_archivo = os.path.join(carpeta_siatf, archivo)
                
                try:
                    with open(ruta_archivo, 'rb') as f:
                        response_data, response_status = procesar_carga_siatf(f, dependencia)

                    if response_status == status.HTTP_201_CREATED:
                        shutil.move(ruta_archivo, os.path.join(carpeta_destino_siatf, archivo))
                    else:
                        resultados.append({
                            'tipo': 'Carga SIATF',
                            'dependencia': dependencia,
                            'error': response_data.get('detalle') or 'No se pudo procesar el archivo'
                        })
                except Exception as e:
                    resultados.append({
                        'tipo': 'Carga SIATF',
                        'dependencia': dependencia,
                        'error': str(e)
                    })
        return Response(resultados, status=status.HTTP_200_OK)  




