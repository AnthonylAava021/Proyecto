#!/usr/bin/env python3
"""
UPSBet - Verificador de Instalación
====================================
Script para verificar que todos los componentes necesarios estén instalados
y configurados correctamente.
"""

import sys
import os
import importlib
from pathlib import Path

def check_python_version():
    """Verificar versión de Python"""
    print("🐍 Verificando versión de Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} no es compatible. Se requiere Python 3.8+")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def check_dependencies():
    """Verificar dependencias de Python"""
    print("\n📦 Verificando dependencias...")
    required_packages = [
        'flask', 'flask_cors', 'psycopg2', 'sklearn', 
        'pandas', 'numpy', 'lightgbm', 'xgboost',
        'joblib', 'requests', 'dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NO INSTALADO")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Paquetes faltantes: {', '.join(missing_packages)}")
        print("Ejecuta: pip install -r requirements.txt")
        return False
    
    print("✅ Todas las dependencias están instaladas")
    return True

def check_model_files():
    """Verificar archivos de modelos"""
    print("\n🤖 Verificando archivos de modelos...")
    model_files = [
        'modelos/modelo_ligapro.pkl',
        'modelos/prediccion_corners_totales.pkl',
        'modelos/modelo_lightgbm_final.pkl',
        'modelos/escalador_corners.pkl'
    ]
    
    missing_files = []
    for file_path in model_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path} ({size:,} bytes)")
        else:
            print(f"❌ {file_path} - NO ENCONTRADO")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Archivos faltantes: {len(missing_files)}")
        return False
    
    print("✅ Todos los archivos de modelos están presentes")
    return True

def check_database_connection():
    """Verificar conexión a la base de datos"""
    print("\n🗄️  Verificando conexión a PostgreSQL...")
    try:
        import psycopg2
        conn = psycopg2.connect(
            host='localhost',
            user='user',
            password='ups_bet05',
            database='UPS_BET',
            port=5432
        )
        conn.close()
        print("✅ Conexión a PostgreSQL exitosa")
        return True
    except Exception as e:
        print(f"❌ Error conectando a PostgreSQL: {e}")
        print("\n📋 Para configurar PostgreSQL:")
        print("1. Instalar PostgreSQL desde https://postgresql.org")
        print("2. Ejecutar: psql -U postgres -f setup_database.sql")
        print("3. O configurar manualmente:")
        print("   - Base de datos: UPS_BET")
        print("   - Usuario: user")
        print("   - Contraseña: ups_bet05")
        return False

def check_data_files():
    """Verificar archivos de datos SQL"""
    print("\n📊 Verificando archivos de datos...")
    data_files = [
        'data/datos_tabla_corners.sql',
        'data/datos_tabla_ganador_resultado.sql',
        'data/datos_tabla_historico_resultado.sql',
        'data/datos_tabla_tarjetas.sql'
    ]
    
    missing_files = []
    for file_path in data_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path} ({size:,} bytes)")
        else:
            print(f"❌ {file_path} - NO ENCONTRADO")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Archivos de datos faltantes: {len(missing_files)}")
        print("Estos archivos son necesarios para importar datos a la base de datos")
        return False
    
    print("✅ Todos los archivos de datos están presentes")
    return True

def check_web_files():
    """Verificar archivos web"""
    print("\n🌐 Verificando archivos web...")
    web_files = [
        'public/index.html',
        'public/css/styles.css',
        'public/js/script.js'
    ]
    
    missing_files = []
    for file_path in web_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path} ({size:,} bytes)")
        else:
            print(f"❌ {file_path} - NO ENCONTRADO")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Archivos web faltantes: {len(missing_files)}")
        return False
    
    print("✅ Todos los archivos web están presentes")
    return True

def main():
    """Función principal"""
    print("=" * 60)
    print("🔍 UPSBet - Verificador de Instalación")
    print("=" * 60)
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_model_files(),
        check_database_connection(),
        check_data_files(),
        check_web_files()
    ]
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)
    
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print("🎉 ¡TODAS LAS VERIFICACIONES PASARON!")
        print("✅ Tu instalación está lista para usar")
        print("\n🚀 Para iniciar el servidor:")
        print("1. Activar entorno virtual: venv\\Scripts\\activate")
        print("2. Ejecutar: python app.py")
        print("3. Abrir: http://localhost:5000")
    else:
        print(f"⚠️  {passed}/{total} verificaciones pasaron")
        print("❌ Hay problemas que necesitan ser resueltos")
        print("\n📖 Revisa el README.md para instrucciones detalladas")
    
    print("=" * 60)
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
