# Sistema de Indicadores Fiscales

## 📋 Descripción

Sistema de gestión y análisis de indicadores fiscales desarrollado en Django (backend) y React (frontend). Permite el procesamiento, almacenamiento y análisis de datos relacionados con la carga laboral de fiscales, plazos de casos y estadísticas del sistema judicial.

---

## 🏗️ Arquitectura del Proyecto

```
INDICADORES/
├── apps/
│   ├── api/                 # Endpoints y lógica de la API REST
│   └── modelos/             # Modelos de datos y migraciones
├── back/                    # Configuración principal de Django
├── data/                    # Archivos de entrada (CSV/Excel)
├── dataprocesada/           # Archivos procesados
├── venv/                    # Entorno virtual de Python
├── frontend/                # Aplicación React (pendiente de implementar)
└── manage.py                # Script de gestión de Django
```

---

## 🚀 Características Principales

### Backend (Django)
- Procesamiento de archivos CSV/Excel con información judicial
- Clasificación automática de plazos (verde, rojo, amarillo)
- Estadísticas de carga laboral por fiscal y dependencia
- Análisis de materia delito y especialidad
- API REST para carga y consulta de datos
- Soporte para múltiples encodings y normalización de caracteres especiales

### Frontend (React) - En desarrollo
- Interfaz de usuario moderna y responsiva
- Dashboard de indicadores en tiempo real
- Formularios para carga de archivos
- Visualización de datos con gráficos y tablas
- Gestión de usuarios y autenticación

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **Framework**: Django 5.2.1
- **API**: Django REST Framework 3.16.0
- **Base de Datos**: PostgreSQL
- **Procesamiento de Datos**: Pandas 2.2.3
- **Autenticación**: Django REST Auth 7.0.1
- **Documentación API**: DRF Spectacular 0.28.0
- **CORS**: django-cors-headers 4.7.0

### Frontend
- **Framework**: React (pendiente de implementar)
- **Gestión de Estado**: Redux/Context API
- **UI Components**: Material-UI o Ant Design
- **HTTP Client**: Axios
- **Routing**: React Router

### Dependencias Principales
```
asgiref==3.8.1
attrs==25.3.0
dj-rest-auth==7.0.1
Django==5.2.1
django-cors-headers==4.7.0
django-filter==25.1
djangorestframework==3.16.0
drf-spectacular==0.28.0
numpy==2.2.6
openpyxl==3.1.5
pandas==2.2.3
psycopg2==2.9.10
xlrd==2.0.1
```

---

## 📦 Instalación

### Prerrequisitos

- Python 3.8+
- Node.js 16+ (para el frontend)
- PostgreSQL
- pip y npm

### Backend (Django)

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

### Frontend (React) - Pendiente

1. **Crear aplicación React**
   ```bash
   npx create-react-app frontend
   cd frontend
   ```

2. **Instalar dependencias**
   ```bash
   npm install axios react-router-dom @mui/material @emotion/react @emotion/styled
   ```

3. **Configurar proxy para desarrollo**
   ```json
   // package.json
   {
     "proxy": "http://localhost:8000"
   }
   ```

4. **Ejecutar servidor de desarrollo**
   ```bash
   npm start
   ```

---

## 📁 Estructura de Archivos

### Formato de Archivos de Entrada

#### Plazos Detallado (CSV/Excel)
```csv
id_fiscal,fiscal,id_unico,etapa,estado,fh_estado,color,plazo,tipo_caso,dias,des_observacion_plazo,dias_paralizacion,dias_total_transcurrido
```
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

---

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

### Plazos
```python
class Plazos(models.Model):
    dentro_plazo = models.IntegerField(default=0)
    por_vencer = models.IntegerField(default=0)
    vencidos = models.IntegerField(default=0)
    dependencia = models.CharField(max_length=256)
    nombre_fiscal = models.CharField(max_length=256)
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_modificacion = models.DateField(auto_now=True)
    tipo_caso = models.CharField(max_length=256)
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

---

## 🔌 Endpoints de la API

### Autenticación
- `POST /api/v1/auth/login/` - Iniciar sesión
- `POST /api/v1/auth/logout/` - Cerrar sesión
- `POST /api/v1/auth/password/reset/` - Restablecer contraseña

### Gestión de Datos
- `POST /api/v1/crearPlazos/` - Crear registros de plazos
- `POST /api/v1/plazos/masivo/` - Carga masiva de plazos
- `POST /api/v1/plazosDetalle` - Carga de plazos detallado
- `POST /api/v1/crearCarga/` - Crear registros de carga laboral
- `POST /api/v1/cargaTotal/` - Crear registros de carga total
- `POST /api/v1/cargaSiatf` - Carga de datos SIATF
- `POST /api/v1/cargaAnio` - Carga de datos anuales

---

## 🧩 Serializers

- **PlazosDetalladoCrearSerializer**: file, dependencia
- **PlazosCrearSerializer**: file, dependencia
- **CargaCrearSerializer**: file, dependencia, mes, anio
- **CargaTotalSerializer**: file, dependencia
- **CargaSiatfSerializer**: file, dependencia
- **CargaAnioCrearSerializer**: file, dependencia, anio

---

## ⚙️ Procesamiento de Archivos

El sistema permite cargar archivos de datos a través de la API o por carpetas locales. El flujo general es:

1. El usuario sube un archivo (CSV/Excel) mediante la API o lo coloca en la carpeta correspondiente
2. El sistema detecta el encoding y normaliza los datos
3. Se procesan los datos y se clasifican según reglas de negocio (por ejemplo, plazos: verde, rojo, amarillo)
4. Los datos procesados se almacenan en la base de datos y los archivos se mueven a la carpeta `dataprocesada/`

### Ejemplo de uso por API

**Plazos Detallado**
```bash
POST /api/v1/plazosDetalle
Content-Type: multipart/form-data
Authorization: Token <tu_token>
file: archivo.csv
dependencia: "FISCALIA PROVINCIAL MIXTA DE MAZUKO"
```

**Carga Laboral**
```bash
POST /api/v1/crearCarga
Content-Type: multipart/form-data
Authorization: Token <tu_token>
file: archivo.xlsx
dependencia: "FISCALIA PROVINCIAL MIXTA DE MAZUKO"
mes: "ENERO"
anio: "2025"
```

---

## 🔒 Seguridad y Autenticación

- Autenticación por token y sesión (configurable en `back/settings.py`)
- Permisos basados en roles de Django
- CORS configurado para permitir comunicación con el frontend
- Validación de archivos y sanitización de datos

---

## 🔧 Configuración

### Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
SECRET_KEY=tu_clave_secreta
DEBUG=True
DATABASE_URL=postgresql://usuario:password@localhost:5432/indicadores
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
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

# Configuración CORS para React
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

---

## 🧠 Funcionalidades Avanzadas

### Backend
- Detección automática de encoding y normalización Unicode
- Clasificación de plazos por colores
- Agrupación inteligente por fiscal, etapa y estado
- Estadísticas por materia delito y especialidad
- Procesamiento masivo de archivos por lotes

### Frontend (Pendiente)
- Dashboard interactivo con gráficos en tiempo real
- Drag & drop para carga de archivos
- Filtros avanzados y búsqueda
- Exportación de reportes en PDF/Excel
- Notificaciones en tiempo real

---

## 🚀 Desarrollo

### Scripts Útiles

**Procesamiento masivo de archivos**
```bash
python apps/api/run_script.py
```

**Crear migraciones**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Ejecutar tests**
```bash
python manage.py test
```

### Estructura de Desarrollo Frontend (Pendiente)

```
frontend/
├── src/
│   ├── components/         # Componentes reutilizables
│   ├── pages/             # Páginas principales
│   ├── services/          # Servicios de API
│   ├── hooks/             # Custom hooks
│   ├── utils/             # Utilidades
│   └── styles/            # Estilos CSS
├── public/
└── package.json
```

---

## ❓ FAQ y Notas

### Preguntas Frecuentes

**¿Cómo manejar archivos con caracteres especiales?**
- El sistema soporta automáticamente archivos en español con caracteres especiales
- Utiliza detección automática de encoding (UTF-8, Latin1, etc.)

**¿Cómo autenticarse en la API?**
- Los endpoints requieren autenticación por token
- Obtener token: `POST /api/v1/auth/login/`
- Incluir en headers: `Authorization: Token <tu_token>`

**¿Dónde se guardan los archivos procesados?**
- Los archivos procesados se mueven automáticamente a la carpeta `dataprocesada/`
- Se organizan por tipo de procesamiento

### Notas de Desarrollo

- El frontend está pendiente de implementar con React
- Considerar usar TypeScript para mejor tipado
- Implementar tests unitarios y de integración
- Configurar CI/CD para despliegue automático

### Contacto

Para dudas técnicas, revisar los comentarios en el código fuente o contactar al desarrollador principal.

---

## 📈 Roadmap

### Próximas Funcionalidades
- [ ] Implementación completa del frontend en React
- [ ] Dashboard con gráficos interactivos
- [ ] Sistema de notificaciones
- [ ] Exportación de reportes
- [ ] API para consultas avanzadas
- [ ] Tests automatizados
- [ ] Documentación de API con Swagger
- [ ] Despliegue en producción