# Sistema de Indicadores Fiscales

## 📋 Descripción

Sistema de gestión y análisis de indicadores fiscales desarrollado en Django que permite el procesamiento, almacenamiento y análisis de datos relacionados con la carga laboral de fiscales, plazos de casos, y estadísticas del sistema judicial.

## 🏗️ Arquitectura del Proyecto

```
INDICADORES/
├── apps/
│   ├── api/                 # API REST endpoints
│   └── modelos/             # Modelos de datos
├── back/                    # Configuración principal de Django
├── data/                    # Datos de entrada
├── dataprocesada/           # Datos procesados
├── venv/                    # Entorno virtual
└── manage.py               # Script de gestión de Django
```

## 🚀 Características Principales

### 📊 Módulos de Procesamiento

1. **Plazos Detallado**
   - Procesamiento de archivos CSV/Excel con información de plazos
   - Clasificación por colores (verde, rojo, amarillo)
   - Agrupación por fiscal, etapa y estado

2. **Carga Laboral**
   - Gestión de casos por fiscal
   - Estadísticas mensuales
   - Análisis de materia delito

3. **Carga Total**
   - Resumen consolidado de trámites
   - Estadísticas por dependencia

4. **Carga SIATF**
   - Procesamiento de datos del sistema SIATF
   - Análisis por especialidad

## 🛠️ Tecnologías Utilizadas

- **Backend**: Django 5.2.1
- **API**: Django REST Framework 3.16.0
- **Base de Datos**: PostgreSQL
- **Procesamiento de Datos**: Pandas 2.2.3
- **Autenticación**: Django REST Auth
- **Documentación API**: DRF Spectacular

## 📦 Instalación

### Prerrequisitos

- Python 3.8+
- PostgreSQL
- pip

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/ronald20R/indicadores.git
   cd indicadores
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar base de datos**
   - Crear base de datos PostgreSQL: `indicadores`
   - Configurar credenciales en `back/settings.py`

5. **Ejecutar migraciones**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Crear superusuario**
   ```bash
   python manage.py createsuperuser
   ```

7. **Ejecutar servidor**
   ```bash
   python manage.py runserver
   ```

## 📊 Modelos de Datos

### PlazosDetalle
```python
class PlazosDetalle(models.Model):
    dependencia = models.CharField(max_length=256)
    nombre_fiscal = models.CharField(max_length=256)
    etapa = models.CharField(max_length=256)
    estado = models.CharField(max_length=256)
    dentro_plazo = models.IntegerField(default=0)
    por_vencer = models.IntegerField(default=0)
    vencidos = models.IntegerField(default=0)
```

### Carga
```python
class Carga(models.Model):
    nombre_fiscal = models.CharField(max_length=256)
    casos_resueltos = models.IntegerField(default=0)
    casos_ingresados = models.IntegerField(default=0)
    casos_en_tramite = models.IntegerField(default=0)
    dependencia = models.CharField(max_length=256)
    fecha = models.DateField(blank=False)
    sentencias = models.IntegerField(default=0)
    archivos_consentidos = models.IntegerField(default=0)
    archivo_califica = models.IntegerField(default=0)
    archivo_preliminar = models.IntegerField(default=0)
```

### CargaTotal
```python
class CargaTotal(models.Model):
    nombre_fiscal = models.CharField(max_length=256)
    total_tramite = models.IntegerField(default=0)
    tramite_historico = models.IntegerField(default=0)
    asignados = models.IntegerField(default=0)
    pendientes = models.IntegerField(default=0)
    calificados = models.IntegerField(default=0)
    dependencia = models.CharField(max_length=256)
    preliminares = models.IntegerField(default=0)
    investigacion_pnp = models.IntegerField(default=0)
    investigacion_preparatoria = models.IntegerField(default=0)
    etapa_intermedia = models.IntegerField(default=0)
    etapa_juzgamiento = models.IntegerField(default=0)
```

## 🔌 API Endpoints

### Plazos
- `POST /api/crearPlazos/` - Crear registros de plazos
- `POST /api/plazos/masivo/` - Carga masiva de plazos
- `POST /api/plazosDetalle` - Carga de plazos detallado

### Carga Laboral
- `POST /api/crearCarga/` - Crear registros de carga laboral

### Carga Total
- `POST /api/cargaTotal/` - Crear registros de carga total

### Carga SIATF
- `POST /api/cargaSiatf` - Carga de datos SIATF

## 📁 Estructura de Archivos

### Formato de Archivos de Entrada

#### Plazos Detallado (CSV/Excel)
```csv
id_fiscal,fiscal,id_unico,etapa,estado,fh_estado,color,plazo,tipo_caso,dias,des_observacion_plazo,dias_paralizacion,dias_total_transcurrido
```

**Columnas requeridas:**
- `fiscal`: Nombre del fiscal
- `etapa`: Etapa del proceso
- `estado`: Estado específico
- `color`: Clasificación (verde.jpg, rojo.jpg, amarillo.jpg)
- `plazo`: Plazo establecido en días
- `dias`: Días transcurridos

#### Carga Laboral (Excel)
```excel
no_fiscal,fe_ing_caso,fe_conclusion,de_estado,condicion,de_mat_deli
```

## 🔧 Configuración

### Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
SECRET_KEY=tu_clave_secreta
DEBUG=True
DATABASE_URL=postgresql://usuario:password@localhost:5432/indicadores
```

### Configuración de Base de Datos

En `back/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'indicadores',
        'USER': 'postgres',
        'PASSWORD': 'tu_password',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}
```

## 🚀 Uso

### Procesamiento de Archivos

1. **Plazos Detallado**
   ```bash
   # Subir archivo CSV/Excel a través de la API
   POST /api/plazosDetalle
   Content-Type: multipart/form-data
   file: archivo.csv
   dependencia: "FISCALIA PROVINCIAL MIXTA DE MAZUKO"
   ```

2. **Carga Laboral**
   ```bash
   # Subir archivo Excel a través de la API
   POST /api/crearCarga
   Content-Type: multipart/form-data
   file: archivo.xlsx
   dependencia: "FISCALIA PROVINCIAL MIXTA DE MAZUKO"
   mes: "ENERO"
   anio: "2025"
   ```

### Funciones de Procesamiento

#### procesar_archivo_plazos_detallado()
```python
def procesar_archivo_plazos_detallado(file, dependencia):
    """
    Procesa archivos CSV/Excel de plazos detallado.
    
    Args:
        file: Archivo a procesar
        dependencia: Nombre de la dependencia
        
    Returns:
        tuple: (success, message)
    """
```

**Características:**
- Soporte para múltiples encodings (UTF-8, Latin1)
- Normalización de caracteres especiales (ñ, acentos)
- Clasificación automática por colores
- Agrupación por fiscal, etapa y estado

## 🔍 Funcionalidades Avanzadas

### Procesamiento de Caracteres Especiales

El sistema maneja automáticamente:
- Caracteres especiales del español (ñ, á, é, í, ó, ú)
- Normalización Unicode
- Detección automática de encoding

### Clasificación de Plazos

- **Verde**: Casos dentro de plazo
- **Rojo**: Casos vencidos
- **Amarillo**: Casos por vencer

### Agrupación Inteligente

- Agrupación por fiscal, etapa y estado
- Consolidación de estadísticas
- Eliminación de duplicados

## 🧪 Testing

```bash
# Ejecutar tests
python manage.py test

# Ejecutar tests específicos
python manage.py test apps.api.tests
```

## 📈 Monitoreo y Logs

El sistema incluye:
- Logs de procesamiento
- Validación de datos
- Manejo de errores
- Estadísticas de procesamiento

## 🔒 Seguridad

- Autenticación por token
- Permisos por modelo
- Validación de archivos
- Sanitización de datos

## 🚀 Despliegue

### Producción

1. **Configurar variables de entorno**
2. **Configurar base de datos de producción**
3. **Ejecutar migraciones**
4. **Configurar servidor web (nginx, gunicorn)**

### Docker (Opcional)

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👥 Autores

- **Ronald** - *Desarrollo inicial* - [ronald20R](https://github.com/ronald20R)

## 🙏 Agradecimientos

- Equipo de desarrollo
- Contribuidores del proyecto
- Comunidad Django

## 📞 Soporte

Para soporte técnico o preguntas:
- Crear un issue en GitHub
- Contactar al equipo de desarrollo

---

**Versión**: 1.0.0  
**Última actualización**: Enero 2025