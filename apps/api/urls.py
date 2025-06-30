from django.urls import path
from .views import CrearCargaSiatfView, CrearPlazosView, CargarCargaLaboralView, CrearCargaTotalView,CrearPlazosDetalleView,CrearCargaAnioView
from .viewss import ProcesarArchivosPlazosView


urlpatterns = ([
    
    path('crearPlazos/', CrearPlazosView.as_view(), name='Crear Plazos'),
    path('crearCarga/', CargarCargaLaboralView.as_view(), name='Crear Carga'),
    path('cargaTotal/', CrearCargaTotalView.as_view(), name='Carga total'),
    path('plazos/masivo/', ProcesarArchivosPlazosView.as_view(), name ='Cargar Plazos de forma masiva'),
    path('cargaSiatf',CrearCargaSiatfView.as_view(), name ='Cargar Carga SIATF de forma masiva'),
    path('plazosDetalle',CrearPlazosDetalleView.as_view(), name ='Cargar Plazos Detallado de forma masiva'),
    path('cargaAnio',CrearCargaAnioView.as_view(), name ='Cargar Carga Anio de forma masiva'),

])