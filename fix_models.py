#!/usr/bin/env python3
"""
Script para verificar y solucionar problemas con los modelos de predicción
"""

import os
import pickle
import sys
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

def check_model_files():
    """Verificar si los archivos de modelo existen"""
    print("🔍 Verificando archivos de modelo...")
    
    models_path = "modelos"
    required_files = ["escalador_corners.pkl", "prediccion_corners_totales.pkl"]
    
    if not os.path.exists(models_path):
        print(f"❌ La carpeta '{models_path}' no existe")
        os.makedirs(models_path)
        print(f"✅ Carpeta '{models_path}' creada")
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(models_path, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Faltan archivos: {missing_files}")
        return False
    
    print("✅ Todos los archivos de modelo existen")
    return True

def test_load_models():
    """Probar cargar los modelos"""
    print("\n🔍 Probando carga de modelos...")
    
    try:
        # Intentar cargar escalador
        with open('modelos/escalador_corners.pkl', 'rb') as f:
            scaler = pickle.load(f)
        print("✅ Escalador cargado correctamente")
        
        # Intentar cargar modelo
        with open('modelos/prediccion_corners_totales.pkl', 'rb') as f:
            model = pickle.load(f)
        print("✅ Modelo de predicción cargado correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error cargando modelos: {e}")
        return False

def create_dummy_models():
    """Crear modelos dummy para pruebas"""
    print("\n🔧 Creando modelos dummy para pruebas...")
    
    try:
        # Crear escalador dummy
        scaler = StandardScaler()
        dummy_data = np.random.rand(100, 10)  # 100 muestras, 10 características
        scaler.fit(dummy_data)
        
        # Crear modelo dummy
        model = RandomForestRegressor(n_estimators=10, random_state=42)
        dummy_X = np.random.rand(100, 10)
        dummy_y = np.random.randint(5, 15, 100)  # Corners entre 5 y 15
        model.fit(dummy_X, dummy_y)
        
        # Guardar modelos
        with open('modelos/escalador_corners.pkl', 'wb') as f:
            pickle.dump(scaler, f)
        
        with open('modelos/prediccion_corners_totales.pkl', 'wb') as f:
            pickle.dump(model, f)
        
        print("✅ Modelos dummy creados y guardados")
        return True
        
    except Exception as e:
        print(f"❌ Error creando modelos dummy: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Verificando y solucionando problemas con modelos...")
    print("=" * 60)
    
    # Verificar archivos
    if not check_model_files():
        print("\n❌ Faltan archivos de modelo")
        response = input("¿Crear modelos dummy para pruebas? (s/n): ")
        if response.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            if create_dummy_models():
                print("\n✅ Modelos dummy creados exitosamente")
            else:
                print("\n❌ No se pudieron crear los modelos dummy")
                sys.exit(1)
        else:
            print("\n❌ No se pueden crear modelos dummy")
            sys.exit(1)
    
    # Probar carga
    if not test_load_models():
        print("\n❌ Los modelos no se pueden cargar")
        response = input("¿Recrear modelos dummy? (s/n): ")
        if response.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            if create_dummy_models():
                print("\n✅ Modelos recreados exitosamente")
                if test_load_models():
                    print("\n✅ Los modelos ahora funcionan correctamente")
                else:
                    print("\n❌ Los modelos siguen sin funcionar")
                    sys.exit(1)
            else:
                print("\n❌ No se pudieron recrear los modelos")
                sys.exit(1)
        else:
            print("\n❌ No se pueden recrear los modelos")
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Todos los modelos están funcionando correctamente!")
    print("\n💡 Ahora puedes ejecutar el servidor:")
    print("   python run_server.py")

if __name__ == "__main__":
    main()
