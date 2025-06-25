import io
import locale
import traceback
from calendar import monthrange
from datetime import datetime, timedelta
import chardet
from rest_framework import  status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
import pandas as pd

from apps.modelos.models import Plazos, Carga, MateriaDelito, CargaTotal, TramitesMensual, CargaSiatf ,PlazosDetalle      
from .serializers import PlazosCrearSerializer, CargaCrearSerializer, CargaTotalSerializer, CargaSiatfSerializer,PlazosDetalladoCrearSerializer

class CrearPlazosDetalleView(CreateAPIView):
    queryset = Plazos.objects.all()
    serializer_class = PlazosDetalladoCrearSerializer
    parser_classes = [MultiPartParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data) 
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        dependencia = serializer.validated_data['dependencia']
        try:
            filename = file.name.lower()
            if filename.endswith('.csv'):
                file.seek(0)
                raw_data = file.read()
                detected = chardet.detect(raw_data)
                encoding_detected = detected['encoding'] or 'latin1'
                
                try:
                    decoded_data = raw_data.decode(encoding_detected, errors='replace')
                    df = pd.read_csv(io.StringIO(decoded_data), sep=',', on_bad_lines='skip')
                except Exception as e:
                    return Response({'error': f'Error al leer CSV: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                excel_df = pd.read_excel(file)
                csv_buffer = io.StringIO()
                excel_df.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)
                df = pd.read_csv(csv_buffer)

            df.columns = df.columns.str.strip()
            
            # Limpiar datos
            df['fiscal'] = df['fiscal'].astype(str).str.strip()
            df['etapa'] = df['etapa'].astype(str).str.strip()
            df['estado'] = df['estado'].astype(str).str.strip()
            df['color'] = df['color'].astype(str).str.strip()
            df['plazo'] = pd.to_numeric(df['plazo'], errors='coerce').fillna(0)
            df['dias'] = pd.to_numeric(df['dias'], errors='coerce').fillna(0)
            
            # Agrupar por fiscal, etapa y estado para contar casos
            conteo_casos = df.groupby(['fiscal', 'etapa', 'estado']).size().reset_index(name='cantidad')
            
            for _, row in conteo_casos.iterrows():
                fiscal = row['fiscal']
                etapa = row['etapa']
                estado = row['estado']
                cantidad = row['cantidad']
                
                # Filtrar datos para este fiscal, etapa y estado específicos
                datos_filtrados = df[
                    (df['fiscal'] == fiscal) & 
                    (df['etapa'] == etapa) & 
                    (df['estado'] == estado)
                ]
                
                # Calcular estadísticas de plazos
                dentro_plazo = 0
                por_vencer = 0
                vencidos = 0
                
                for _, caso in datos_filtrados.iterrows():
                    dias_transcurridos = caso['dias']
                    plazo_establecido = caso['plazo']
                    color = caso['color']
                    
                    # Lógica para clasificar según el estado del plazo
                    if color == 'verde.jpg':
                        # Caso dentro de plazo
                        dentro_plazo += 1
                    elif color == 'rojo.jpg':
                        # Caso vencido
                        vencidos += 1
                    else:
                        # Caso por vencer (amarillo o sin color específico)
                        if dias_transcurridos < plazo_establecido:
                            por_vencer += 1
                        else:
                            vencidos += 1
                
                # Solo crear registro si hay casos
                if dentro_plazo > 0 or por_vencer > 0 or vencidos > 0:
                    PlazosDetalle.objects.create(
                        dependencia=dependencia,
                        nombre_fiscal=fiscal,
                        etapa=etapa,
                        estado=estado,
                        dentro_plazo=dentro_plazo,
                        por_vencer=por_vencer,
                        vencidos=vencidos
                    )
            
            return Response({'mensaje': 'Datos cargados correctamente.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
class CrearPlazosView(CreateAPIView):
    queryset = Plazos.objects.all()
    serializer_class = PlazosCrearSerializer
    parser_classes = [MultiPartParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        dependencia = serializer.validated_data['dependencia']
        try:
            # Detecta el tipo de archivo y lo convierte a CSV en memoria
            filename = file.name.lower()
            if filename.endswith('.csv'):
                file.seek(0)
                df = pd.read_csv(file, encoding='latin1', sep=',', on_bad_lines='skip')
                # df = pd.read_csv(file, encoding='latin1', delimiter=';')
            else:
                # Lee el archivo Excel y lo convierte a CSV en memoria
                excel_df = pd.read_excel(file)
                csv_buffer = io.StringIO()
                excel_df.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)
                df = pd.read_csv(csv_buffer)

            df.columns = df.columns.str.strip()  # Limpia los nombres de columnas
            tipos = [
                'Calificación','Investigación Preliminar(Fiscal)','Investigación Preliminar(P.N.P.)',
                'Investigación Preparatoria','Conclusión de Investigación','Investigación Preliminar Pérdida Dominio'
            ]

            for _, row in df.iterrows():
                for i in range(1, 7):
                    v_key, a_key, r_key = f'v{i}', f'a{i}', f'r{i}'
                    if f'v{i}' in df.columns and f'a{i}' in df.columns and f'r{i}' in df.columns:
                        v_val = row[v_key]
                        a_val = row[a_key]
                        r_val = row[r_key]

                        # Si todos son 0, saltar a la siguiente iteración
                        if v_val==0 and a_val==0 and r_val==0:
                            continue
                        Plazos.objects.create(
                            dentro_plazo=row[f'v{i}'],
                            por_vencer=row[f'a{i}'],
                            vencidos=row[f'r{i}'],
                            nombre_fiscal=f"{row['ap_fiscal']} {row['no_fiscal']}",
                            dependencia=dependencia,
                            tipo_caso=tipos[i-1] if i-1 < len(tipos) else None
                        )
            return Response({'mensaje': 'Datos cargados correctamente.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CargarCargaLaboralView(CreateAPIView):
    parser_classes = [MultiPartParser]
    serializer_class = CargaCrearSerializer
    queryset = Carga.objects.all()

    def create(self, request, *args, **kwargs):
        locale.setlocale(locale.LC_TIME, 'es-ES')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data['file']
        dependencia = serializer.validated_data['dependencia']
        mes = serializer.validated_data['mes']
        anio = serializer.validated_data['anio']

        try:

            try:
                df = pd.read_excel(file)

            except Exception as e:
                error_message = f"{str(e)}\n{traceback.format_exc()}"
                return Response({'error': f'Error al leer Excel:\n{error_message}'}, status=status.HTTP_400_BAD_REQUEST)

            df = df.rename(columns={
                'no_fiscal': 'nombre_fiscal',
                'fe_ing_caso': 'fecha_ingreso',
                'fe_conclusion': 'fecha_conclusion',
                'de_estado': 'estado',
                'condicion': 'condicion',
                'de_mat_deli': 'materia_delito'
            })

            df['estado'] = (
                df['estado']
                .astype(str)
                .str.upper()
                .str.normalize('NFKD')
                .str.encode('ascii', errors='ignore')
                .str.decode('utf-8')
                .str.strip()
            )
            df['condicion'] = df['condicion'].astype(str).str.strip().str.upper()
            df['nombre_fiscal'] = df['nombre_fiscal'].astype(str).str.strip().str.upper()
            df['materia_delito'] = df['materia_delito'].astype(str).str.strip().str.upper()

            inicio_mes = datetime(anio, mes, 1)
            mes_anterior = (inicio_mes - timedelta(days=1)).replace(day=1)

            rangos = [
                (inicio_mes.strftime('%B').upper(), inicio_mes.date(), (inicio_mes + pd.offsets.MonthEnd(0)).date()),
                (mes_anterior.strftime('%B').upper(), mes_anterior.date(),
                 (mes_anterior + pd.offsets.MonthEnd(0)).date())
            ]

            df['fecha_ingreso'] = pd.to_datetime(df['fecha_ingreso'], dayfirst=True, errors='coerce').dt.date
            df['fecha_conclusion'] = pd.to_datetime(df['fecha_conclusion'], dayfirst=True, errors='coerce').dt.date
            inicio_mes = datetime(anio, mes, 1).date()
            ultimo_dia = monthrange(anio, mes)[1]
            fin_mes = datetime(anio, mes, ultimo_dia).date()
            dias_mes = [inicio_mes + timedelta(days=i) for i in range((fin_mes - inicio_mes).days + 1)]

            fiscales = df['nombre_fiscal'].dropna().unique()
            for label, inicio, fin in rangos:
                df_filtrado = df[(df['fecha_ingreso'] >= inicio) & (df['fecha_ingreso'] <= fin)]
                conteo = df_filtrado['materia_delito'].value_counts()
                for materia, cantidad in conteo.items():
                    MateriaDelito.objects.create(
                        materia=materia,
                        cantidad=cantidad,
                        mes=label,
                        dependencia = dependencia
                    )

            # Agrupar por fiscal solo del mes actual
            df_mes_actual = df[(df['fecha_ingreso'] >= inicio_mes) & (df['fecha_ingreso'] <= fin_mes)]
            df_mes_actual['estado'] = df_mes_actual['estado'].astype(str).str.strip().str.upper()

            conteo_fiscales = df_mes_actual.groupby('nombre_fiscal').agg(
                total_tramite=('estado', 'count'),
                resuelto_mes=('estado', lambda x: (x=='RESUELTO').sum()),
                tramite_mes=('estado', lambda x: (x=='EN TRAMITE').sum()),
                fecha_ingreso=('fecha_ingreso', 'min'),
                fecha_conclusion=('fecha_conclusion', 'max'),
            ).reset_index()

            nombre_mes = inicio_mes.strftime('%B').upper()

            for _, row in conteo_fiscales.iterrows():
                TramitesMensual.objects.update_or_create(
                    dependencia=dependencia,
                    nombre_fiscal=row['nombre_fiscal'],
                    mes=nombre_mes,
                    defaults={
                        'fecha_ingreso': row['fecha_ingreso'],
                        'fecha_conclusion': row['fecha_conclusion'],
                        'total_tramite': row['total_tramite'],
                        'tramite_mes': row['tramite_mes'],
                        'resuelto_mes': row['resuelto_mes'],
                    }
                )

            for fiscal in fiscales:
                registros_fiscal = df[df['nombre_fiscal'] == fiscal]

                for dia in dias_mes:
                    casos_resueltos = registros_fiscal[
                        (registros_fiscal['condicion'] == 'RESUELTO') &
                        (registros_fiscal['fecha_conclusion'] == dia)
                        ].shape[0]

                    casos_ingresados = registros_fiscal[
                        registros_fiscal['fecha_ingreso'] == dia
                        ].shape[0]

                    casos_en_tramite = registros_fiscal[
                        (registros_fiscal['condicion'] == 'EN TRAMITE') &
                        (registros_fiscal['fecha_ingreso'] == dia)
                        ].shape[0]

                    archivos_preliminar = registros_fiscal[
                        (registros_fiscal['estado'] == 'CON ARCHIVO (PRELIMINAR)') &
                        (registros_fiscal['fecha_conclusion'] == dia)
                        ].shape[0]

                    archivo_califica = registros_fiscal[
                        (registros_fiscal['estado'] == 'CON ARCHIVO (CALIFICA)') &
                        (registros_fiscal['fecha_conclusion'] == dia)
                        ].shape[0]

                    archivos_consentidos = registros_fiscal[
                        (registros_fiscal['estado'] == 'ARCHIVO CONSENTIDO') &
                        (registros_fiscal['fecha_conclusion'] == dia)
                        ].shape[0]

                    sentencias = registros_fiscal[
                        (registros_fiscal['estado'] == 'CON SENTENCIA') &
                        (registros_fiscal['fecha_conclusion'] == dia)
                        ].shape[0]
                    if any([
                        casos_resueltos, casos_ingresados, casos_en_tramite,
                        archivos_preliminar, archivo_califica, archivos_consentidos, sentencias
                    ]):
                        # Crear registro
                        Carga.objects.create(
                            nombre_fiscal=fiscal,
                            casos_resueltos=casos_resueltos,
                            casos_ingresados=casos_ingresados,
                            casos_en_tramite=casos_en_tramite,
                            dependencia=dependencia,
                            fecha=dia,
                            sentencias=sentencias,
                            archivos_consentidos=archivos_consentidos,
                            archivo_califica=archivo_califica,
                            archivo_preliminar=archivos_preliminar
                        )

            return Response({'mensaje': 'Carga laboral del mes procesada correctamente.'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CrearCargaTotalView(CreateAPIView):
    queryset = CargaTotal.objects.all()
    serializer_class = CargaTotalSerializer
    parser_classes = [MultiPartParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data['file']
        dependencia = serializer.validated_data['dependencia']

        try:
            file.seek(0)
            raw_data = file.read()
            detected = chardet.detect(raw_data)
            encoding_detected = detected['encoding'] or 'latin1'

            try:
                decoded_data = raw_data.decode(encoding_detected, errors='replace')
                df = pd.read_csv(io.StringIO(decoded_data), sep=',', on_bad_lines='skip')
            except Exception as e:
                return Response({'error': f'Error al leer CSV: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
            df.columns = df.columns.str.strip()


            for _, row in df.iterrows():
                asignados = row.get('asig', 0)
                total_tramite = row.get('pend', 0)+row.get('calif', 0)+row.get('preli', 0)+row.get('pnp', 0)+row.get('prepa', 0)+row.get('inter', 0)+row.get('juzga', 0)
                tramite_historico = asignados - total_tramite

                nombre_fiscal = f"{row.get('apell', '').strip()} {row.get('nomb', '').strip()}"

                CargaTotal.objects.create(
                    nombre_fiscal=nombre_fiscal,
                    total_tramite=total_tramite,
                    tramite_historico=tramite_historico,
                    asignados=asignados,
                    pendientes=row.get('pend', 0),
                    calificados=row.get('calif', 0),
                    dependencia=dependencia,
                    preliminares=row.get('preli', 0),
                    investigacion_pnp=row.get('pnp', 0),
                    investigacion_preparatoria=row.get('prepa', 0),
                    etapa_intermedia=row.get('inter', 0),
                    etapa_juzgamiento=row.get('juzga', 0),
                )

            return Response({'mensaje': 'Carga total registrada correctamente.'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CrearCargaSiatfView(CreateAPIView):
    queryset = CargaSiatf.objects.all()
    serializer_class = CargaSiatfSerializer
    parser_classes = [MultiPartParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data['file']
        dependencia = serializer.validated_data['dependencia']

        try: 
            file.seek(0)
            raw_data = file.read()
            detected = chardet.detect(raw_data)
            encoding_detected = detected['encoding'] or 'latin1'

            try:
                df = pd.read_excel(file)            
            except Exception as e:
                return Response({'error': f'Error al leer Excel: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

            # Debug: imprimir columnas del DataFrame
            print("Columnas originales:", df.columns.tolist())

            df = df.rename(columns={
                'de_esp': 'Especialidad',
                'de_estado': 'Estado'
            })

            df.columns = df.columns.str.strip()  
            
            # Debug: imprimir columnas después del rename
            print("Columnas después del rename:", df.columns.tolist())

            # Limpiar datos
            df['Especialidad'] = df['Especialidad'].astype(str).str.strip()
            df['Estado'] = df['Estado'].astype(str).str.strip()
            
            # Debug: verificar si hay datos en las columnas
            print("Valores únicos en Especialidad:", df['Especialidad'].unique())
            print("Valores únicos en Estado:", df['Estado'].unique())

            # Contar casos por especialidad y estado
            conteo_casos = df.groupby(['Especialidad', 'Estado']).size().reset_index(name='cantidad')
            
            # Debug: imprimir el conteo
            print("Conteo de casos:", conteo_casos.to_dict('records'))

            for _, row in conteo_casos.iterrows():
                print(f"Procesando: Especialidad={row['Especialidad']}, Estado={row['Estado']}, Cantidad={row['cantidad']}")
                CargaSiatf.objects.update_or_create(
                    dependencia=dependencia,
                    especialidad=row['Especialidad'],
                    estado=row['Estado'],
                    defaults={'cantidad': row['cantidad'],
                              'casos_ingresados': row['cantidad']}  
                )

            return Response({'mensaje': 'Carga SIATF registrada correctamente.'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)





