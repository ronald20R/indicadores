import io
import locale
import traceback
from calendar import monthrange
from datetime import datetime, timedelta

import pandas as pd
from django.db import transaction
import chardet
from rest_framework import status


from apps.modelos.models import Plazos, Carga, TramitesMensual, MateriaDelito, CargaTotal, CargaSiatf,PlazosDetalle

@transaction.atomic
def procesar_archivo_plazos_detallado(file, dependencia):
    try:
        file.seek(0)
        raw_data = file.read()
        detected = chardet.detect(raw_data)
        encoding_detected = detected['encoding'] or 'latin1'

        # Intentar diferentes codificaciones si la primera falla
        encodings_to_try = [encoding_detected, 'utf-8', 'latin1', 'cp1252', 'iso-8859-1', 'windows-1252']
        
        df = None
        for encoding in encodings_to_try:
            try:
                # Intentar decodificar sin reemplazar caracteres
                decoded_data = raw_data.decode(encoding)
                df = pd.read_csv(io.StringIO(decoded_data), sep=',', on_bad_lines='skip')
                break
            except UnicodeDecodeError:
                continue
            except Exception:
                continue
        
        if df is None:
            return False, 'No se pudo leer el archivo con ninguna codificación conocida'

        df.columns = df.columns.str.strip()
        
        # Limpiar datos - manejar caracteres especiales correctamente
        df['fiscal'] = df['fiscal'].astype(str).str.strip()
        df['etapa'] = df['etapa'].astype(str).str.strip()
        df['estado'] = df['estado'].astype(str).str.strip()
        df['color'] = df['color'].astype(str).str.strip()
        df['plazo'] = pd.to_numeric(df['plazo'], errors='coerce').fillna(0)
        df['dias'] = pd.to_numeric(df['dias'], errors='coerce').fillna(0)
        
        # Función para clasificar el estado del plazo
        def clasificar_estado_plazo(color, dias_transcurridos, plazo_establecido):
            if pd.isna(color) or color == '':
                # Si no hay color, usar la lógica de días
                if dias_transcurridos < plazo_establecido:
                    return 'por_vencer'
                else:
                    return 'vencidos'
            
            color_lower = color.lower().strip()
            if 'verde' in color_lower:
                return 'dentro_plazo'
            elif 'rojo' in color_lower:
                return 'vencidos'
            elif 'amarillo' in color_lower:
                return 'por_vencer'
            else:
                # Si no reconoce el color, usar la lógica de días
                if dias_transcurridos < plazo_establecido:
                    return 'por_vencer'
                else:
                    return 'vencidos'
        
        # Aplicar clasificación a cada fila
        df['estado_plazo'] = df.apply(
            lambda row: clasificar_estado_plazo(row['color'], row['dias'], row['plazo']), 
            axis=1
        )
        
        # Agrupar por fiscal, etapa y estado para contar casos
        conteo_casos = df.groupby(['fiscal', 'etapa', 'estado', 'estado_plazo']).size().reset_index(name='cantidad')
        
        # Crear un diccionario para acumular los conteos
        resultados = {}
        
        for _, row in conteo_casos.iterrows():
            fiscal = row['fiscal']
            etapa = row['etapa']
            estado = row['estado']
            estado_plazo = row['estado_plazo']
            cantidad = row['cantidad']
            
            # Crear clave única para cada combinación
            clave = (fiscal, etapa, estado)
            
            if clave not in resultados:
                resultados[clave] = {
                    'fiscal': fiscal,
                    'etapa': etapa,
                    'estado': estado,
                    'dentro_plazo': 0,
                    'por_vencer': 0,
                    'vencidos': 0
                }
            
            # Acumular conteos según el estado del plazo
            if estado_plazo == 'dentro_plazo':
                resultados[clave]['dentro_plazo'] += cantidad
            elif estado_plazo == 'por_vencer':
                resultados[clave]['por_vencer'] += cantidad
            elif estado_plazo == 'vencidos':
                resultados[clave]['vencidos'] += cantidad
        
        # Crear registros en la base de datos
        registros_creados = 0
        for clave, datos in resultados.items():
            # Solo crear registro si hay casos
            if datos['dentro_plazo'] > 0 or datos['por_vencer'] > 0 or datos['vencidos'] > 0:
                PlazosDetalle.objects.create(
                    dependencia=dependencia,
                    nombre_fiscal=datos['fiscal'],
                    etapa=datos['etapa'],
                    estado=datos['estado'],
                    dentro_plazo=datos['dentro_plazo'],
                    por_vencer=datos['por_vencer'],
                    vencidos=datos['vencidos']
                )
                registros_creados += 1
        
        return True, f'Datos cargados correctamente. Se crearon {registros_creados} registros.'
    except Exception as e:
        return False, f'Error en el procesamiento: {str(e)}'




@transaction.atomic
def procesar_archivo_plazos(file, dependencia):
    try:
        file.seek(0)
        raw_data = file.read()
        detected = chardet.detect(raw_data)
        encoding_detected = detected['encoding'] or 'latin1'

        try:
            decoded_data = raw_data.decode(encoding_detected, errors='replace')
            df = pd.read_csv(io.StringIO(decoded_data), sep=',', on_bad_lines='skip')
        except Exception as e:
            return False, f'Error al leer CSV: {str(e)}'

        df.columns = df.columns.str.strip()

        tipos = [
            'Calificación','Investigación Preliminar(Fiscal)','Investigación Preliminar(P.N.P.)',
            'Investigación Preparatoria','Conclusión de Investigación','Investigación Preliminar Pérdida Dominio'
        ]

        for _, row in df.iterrows():
            for i in range(1, 7):
                v_key, a_key, r_key = f'v{i}', f'a{i}', f'r{i}'
                if v_key in df.columns and a_key in df.columns and r_key in df.columns:
                    v_val = row[v_key]
                    a_val = row[a_key]
                    r_val = row[r_key]
                    if v_val == 0 and a_val == 0 and r_val == 0:
                        continue
                    Plazos.objects.create(
                        dentro_plazo=v_val,
                        por_vencer=a_val,
                        vencidos=r_val,
                        nombre_fiscal=f"{row['ap_fiscal']} {row['no_fiscal']}",
                        dependencia=dependencia,
                        tipo_caso=tipos[i-1] if i-1 < len(tipos) else None
                    )
        return True, 'Datos cargados correctamente.'
    except Exception as e:
        return False, str(e)


@transaction.atomic
def procesar_carga_laboral(file, dependencia, mes, anio):
    anio = int(anio)
    mes = int(mes)
    try:
        locale.setlocale(locale.LC_TIME, 'es-ES')


        try:
            df = pd.read_excel(file,engine='xlrd')
        except Exception as e:
            error_message = f"{str(e)}\n{traceback.format_exc()}"
            return {'error': f'Error al leer Excel:\n{error_message}'}, status.HTTP_400_BAD_REQUEST

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
            (mes_anterior.strftime('%B').upper(), mes_anterior.date(), (mes_anterior + pd.offsets.MonthEnd(0)).date())
        ]

        df['fecha_ingreso'] = pd.to_datetime(df['fecha_ingreso'], dayfirst=True, errors='coerce').dt.date
        df['fecha_conclusion'] = pd.to_datetime(df['fecha_conclusion'], dayfirst=True, errors='coerce').dt.date
        inicio_mes = datetime(anio, mes, 1).date()
        ultimo_dia = monthrange(anio, mes)[1]
        fin_mes = datetime(anio, mes, ultimo_dia).date()
        dias_mes = [inicio_mes + timedelta(days=i) for i in range((fin_mes - inicio_mes).days + 1)]

        fiscales = df['nombre_fiscal'].dropna().unique()

        # Guardar conteo por materia delito para mes actual y anterior
        for label, inicio, fin in rangos:
            df_filtrado = df[(df['fecha_ingreso'] >= inicio) & (df['fecha_ingreso'] <= fin)]
            conteo = df_filtrado['materia_delito'].value_counts()
            for materia, cantidad in conteo.items():
                MateriaDelito.objects.create(
                    materia=materia,
                    cantidad=cantidad,
                    mes=label,
                    dependencia=dependencia
                )

        # Filtrar registros solo del mes actual
        df_mes_actual = df[(df['fecha_ingreso'] >= inicio_mes) & (df['fecha_ingreso'] <= fin_mes)].copy()

        df_mes_actual['fecha_ingreso_valida'] = pd.to_datetime(df_mes_actual['fecha_ingreso'], errors='coerce')

        errores_ingreso = df_mes_actual[
            df_mes_actual['fecha_ingreso'].notna() & df_mes_actual['fecha_ingreso_valida'].isna()]

        for _, row in errores_ingreso.iterrows():
            print(f"Error en fecha_ingreso: '{row['fecha_ingreso']}' del fiscal {row['nombre_fiscal']}")

        # Asegurar fechas correctas
        df_mes_actual['fecha_ingreso'] = pd.to_datetime(df_mes_actual['fecha_ingreso'], errors='coerce')
        df_mes_actual['fecha_conclusion'] = pd.to_datetime(df_mes_actual['fecha_conclusion'], errors='coerce')

        # Limpieza de 'estado' y 'condicion'
        df_mes_actual['estado'] = df_mes_actual['estado'].astype(str).str.strip().str.upper()
        df_mes_actual['condicion'] = df_mes_actual['condicion'].astype(str).str.strip().str.upper()

        # Reemplazar NaT por None para evitar problemas
        df_mes_actual['fecha_ingreso'] = df_mes_actual['fecha_ingreso'].where(df_mes_actual['fecha_ingreso'].notna(), None)
        df_mes_actual['fecha_conclusion'] = df_mes_actual['fecha_conclusion'].where(df_mes_actual['fecha_conclusion'].notna(), None)

        # Columnas auxiliares para conteos binarios
        df_mes_actual['resuelto_bin'] = (df_mes_actual['condicion'] == 'RESUELTO').astype(int)
        #(registros_fiscal['condicion'] == 'EN TRAMITE')
        df_mes_actual['tramite_bin'] = (df_mes_actual['condicion'].isin(['EN TRAMITE', 'INVESTIGACION PREVENTIVA'])).astype(int)

        # Agrupar y calcular agregados por fiscal
        conteo_fiscales = df_mes_actual.groupby('nombre_fiscal').agg(
            total_tramite=('estado', 'count'),
            resuelto_mes=('resuelto_bin', 'sum'),
            tramite_mes=('tramite_bin', 'sum'),
            fecha_ingreso=('fecha_ingreso', 'min'),
            fecha_conclusion=('fecha_conclusion', 'max'),
        ).reset_index()

        nombre_mes = inicio_mes.strftime('%B').upper()

        for _, row in conteo_fiscales.iterrows():
            # fecha_ingreso = row['fecha_ingreso']
            # fecha_conclusion = row['fecha_conclusion']

            TramitesMensual.objects.update_or_create(
                dependencia=dependencia,
                nombre_fiscal=row['nombre_fiscal'],
                mes=nombre_mes,
                defaults={
                    # 'fecha_ingreso': fecha_ingreso if pd.notnull(fecha_ingreso) else None,
                    # 'fecha_conclusion': fecha_conclusion if pd.notnull(fecha_conclusion) else None,
                    'total_tramite': row['total_tramite'],
                    'tramite_mes': row['tramite_mes'],
                    'resuelto_mes': row['resuelto_mes'],
                }
            )

        # Crear registros diarios
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
                    #(registros_fiscal['condicion'] == 'EN TRAMITE') |
                    (registros_fiscal['condicion'].isin(['EN TRAMITE', 'INVESTIGACION PREVENTIVA'])) &
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
                fecha_dia = dia if pd.notnull(dia) else None

                if any([
                    casos_resueltos, casos_ingresados, casos_en_tramite,
                    archivos_preliminar, archivo_califica, archivos_consentidos, sentencias
                ]):
                    Carga.objects.create(
                        nombre_fiscal=fiscal,
                        casos_resueltos=casos_resueltos,
                        casos_ingresados=casos_ingresados,
                        casos_en_tramite=casos_en_tramite,
                        dependencia=dependencia,
                        fecha=fecha_dia,
                        sentencias=sentencias,
                        archivos_consentidos=archivos_consentidos,
                        archivo_califica=archivo_califica,
                        archivo_preliminar=archivos_preliminar
                    )

        return {'mensaje': 'Carga laboral del mes procesada correctamente.'}, status.HTTP_201_CREATED


    except Exception as e:


        print("Error general:", e)

        print(traceback.format_exc())

        return {'error': str(e)}, status.HTTP_400_BAD_REQUEST


@transaction.atomic
def procesar_carga_total(file, dependencia):

    try:
        file.seek(0)
        raw_data = file.read()
        detected = chardet.detect(raw_data)
        encoding_detected = detected['encoding'] or 'latin1'

        try:
            decoded_data = raw_data.decode(encoding_detected, errors='replace')
            df = pd.read_csv(io.StringIO(decoded_data), sep=',', on_bad_lines='skip')
        except Exception as e:
            return {'error': f'Error al leer CSV: {str(e)}'}, status.HTTP_400_BAD_REQUEST

        df.columns = df.columns.str.strip()

        for _, row in df.iterrows():
            asignados = row.get('asig', 0)
            total_tramite = (
                    row.get('pend', 0) + row.get('calif', 0) + row.get('preli', 0) +
                    row.get('pnp', 0) + row.get('prepa', 0) + row.get('inter', 0) +
                    row.get('juzga', 0)
            )
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

        return {'mensaje': 'Carga total registrada correctamente.'}, status.HTTP_201_CREATED

    except Exception as e:
        return {'error': str(e)}, status.HTTP_400_BAD_REQUEST

@transaction.atomic
def procesar_carga_siatf(file, dependencia):
    try:
        file.seek(0)
        raw_data = file.read()
        detected = chardet.detect(raw_data)
        encoding_detected = detected['encoding'] or 'latin1'
        
        try:
            df = pd.read_excel(io.BytesIO(raw_data), engine='openpyxl')
        except Exception as e:
            return {'error': f'Error al leer Excel: {str(e)}'}, status.HTTP_400_BAD_REQUEST
        
        df = df.rename(columns={
            'de_esp': 'Especialidad',
            'de_estado': 'Estado'
        })

        df.columns = df.columns.str.strip()
        
        # Limpiar datos
        df['Especialidad'] = df['Especialidad'].astype(str).str.strip()
        df['Estado'] = df['Estado'].astype(str).str.strip()
        
        # Contar casos por especialidad y estado
        conteo_casos = df.groupby(['Especialidad', 'Estado']).size().reset_index(name='cantidad')

        for _, row in conteo_casos.iterrows():
            CargaSiatf.objects.update_or_create(
                dependencia=dependencia,
                especialidad=row['Especialidad'],
                estado=row['Estado'],
                defaults={'cantidad': row['cantidad'],
                         'casos_ingresados': row['cantidad']}
            )

        return {'mensaje': 'Carga SIATF registrada correctamente.'}, status.HTTP_201_CREATED
    except Exception as e:
        return {'error': str(e)}, status.HTTP_400_BAD_REQUEST



