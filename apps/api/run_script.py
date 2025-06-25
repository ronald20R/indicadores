import django
import os
import sys

# Asegura que la carpeta raíz del proyecto está en sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')
django.setup()

from apps.api.procesar_archivos import procesar_archivos

if __name__ == '__main__':
    mes = input("Ingrese el mes (MM): ")
    anio = input("Ingrese el año (YYYY): ")

    resultados = procesar_archivos(mes, anio)

    for r in resultados:
        if 'error' in r:
            print(f"[ERROR] {r['tipo']} - {r['dependencia']}: {r['error']}")
        else:
            print(f"[OK] {r['tipo']} - {r['dependencia']}: {r['mensaje']}")
    input("\nPresiona Enter para salir...")