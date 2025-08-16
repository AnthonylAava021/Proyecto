#!/usr/bin/env python3
"""
Script para iniciar el servidor de desarrollo UPSBet
"""

import os
import sys
import subprocess

def check_dependencies():
    """Verificar que las dependencias estén instaladas"""
    print("🔍 Verificando dependencias...")
    
    try:
        import flask
        import psycopg2
        import pandas
        import numpy
        import sklearn
        print("✅ Todas las dependencias están instaladas")
        return True
    except ImportError as e:
        print(f"❌ Falta dependencia: {e}")
        print("\n💡 Instala las dependencias con:")
        print("   pip install -r requirements.txt")
        return False

def check_models():
    """Verificar que los modelos existan"""
    print("🔍 Verificando modelos...")
    
    models_path = "modelos"
    required_files = ["escalador_corners.pkl", "prediccion_corners_totales.pkl"]
    
    if not os.path.exists(models_path):
        print(f"❌ La carpeta '{models_path}' no existe")
        return False
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(models_path, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Faltan archivos de modelo: {missing_files}")
        return False
    
    print("✅ Todos los modelos están presentes")
    return True

def main():
    """Función principal"""
    print("🚀 Iniciando servidor UPSBet...")
    print("=" * 50)
    
    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)
    
    # Verificar modelos
    if not check_models():
        sys.exit(1)
    
    print("\n🌐 Iniciando servidor web...")
    print("   El frontend estará disponible en: http://localhost:5000")
    print("   El backend API estará en: http://localhost:5000/api/")
    print("\n💡 Para detener el servidor, presiona Ctrl+C")
    print("=" * 50)
    
    # Iniciar el servidor Flask
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n👋 Servidor detenido")
    except Exception as e:
        print(f"\n❌ Error iniciando servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
