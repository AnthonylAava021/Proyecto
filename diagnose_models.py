#!/usr/bin/env python3
"""
Script de diagnóstico para modelos de predicción de corners
"""

import os
import sys
import pickle
import traceback

def check_python_version():
    """Verificar versión de Python"""
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print()

def check_dependencies():
    """Verificar dependencias instaladas"""
    try:
        import sklearn
        print(f"scikit-learn version: {sklearn.__version__}")
    except ImportError as e:
        print(f"scikit-learn not installed: {e}")
    
    try:
        import pandas
        print(f"pandas version: {pandas.__version__}")
    except ImportError as e:
        print(f"pandas not installed: {e}")
    
    try:
        import numpy
        print(f"numpy version: {numpy.__version__}")
    except ImportError as e:
        print(f"numpy not installed: {e}")
    
    print()

def check_model_files():
    """Verificar que los archivos de modelo existen"""
    model_files = [
        'modelos/escalador_corners.pkl',
        'modelos/prediccion_corners_totales.pkl'
    ]
    
    for file_path in model_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✓ {file_path} exists ({size} bytes)")
        else:
            print(f"✗ {file_path} does not exist")
    print()

def test_pickle_loading():
    """Probar carga de pickle con diferentes métodos"""
    print("=== Testing Pickle Loading ===")
    
    # Probar escalador
    print("Testing escalador_corners.pkl:")
    try:
        with open('modelos/escalador_corners.pkl', 'rb') as f:
            scaler = pickle.load(f)
        print(f"✓ Escalador loaded successfully: {type(scaler)}")
        
        # Verificar que es un StandardScaler
        if hasattr(scaler, 'transform'):
            print("✓ Escalador has transform method")
        else:
            print("✗ Escalador missing transform method")
            
    except Exception as e:
        print(f"✗ Error loading escalador: {e}")
        print(f"Error type: {type(e)}")
        traceback.print_exc()
    
    print()
    
    # Probar modelo
    print("Testing prediccion_corners_totales.pkl:")
    try:
        with open('modelos/prediccion_corners_totales.pkl', 'rb') as f:
            model = pickle.load(f)
        print(f"✓ Model loaded successfully: {type(model)}")
        
        # Verificar que es un modelo de sklearn
        if hasattr(model, 'predict'):
            print("✓ Model has predict method")
        else:
            print("✗ Model missing predict method")
            
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        print(f"Error type: {type(e)}")
        traceback.print_exc()
    
    print()

def test_with_different_encodings():
    """Probar con diferentes encodings de pickle"""
    print("=== Testing Different Pickle Encodings ===")
    
    encodings = [None, 'latin1', 'utf8', 'ascii']
    
    for encoding in encodings:
        print(f"Testing with encoding: {encoding}")
        try:
            with open('modelos/escalador_corners.pkl', 'rb') as f:
                if encoding:
                    scaler = pickle.load(f, encoding=encoding)
                else:
                    scaler = pickle.load(f)
            print(f"✓ Escalador loaded with encoding {encoding}")
            break
        except Exception as e:
            print(f"✗ Failed with encoding {encoding}: {e}")
    
    print()
    
    for encoding in encodings:
        print(f"Testing model with encoding: {encoding}")
        try:
            with open('modelos/prediccion_corners_totales.pkl', 'rb') as f:
                if encoding:
                    model = pickle.load(f, encoding=encoding)
                else:
                    model = pickle.load(f)
            print(f"✓ Model loaded with encoding {encoding}")
            break
        except Exception as e:
            print(f"✗ Failed with encoding {encoding}: {e}")
    
    print()

def test_model_compatibility():
    """Probar compatibilidad del modelo con datos de ejemplo"""
    print("=== Testing Model Compatibility ===")
    
    try:
        # Cargar modelos
        with open('modelos/escalador_corners.pkl', 'rb') as f:
            scaler = pickle.load(f)
        
        with open('modelos/prediccion_corners_totales.pkl', 'rb') as f:
            model = pickle.load(f)
        
        # Crear datos de ejemplo (ajustar según las características esperadas)
        import numpy as np
        import pandas as pd
        
        # Crear un DataFrame de ejemplo con columnas típicas
        # Esto es una suposición, ajustar según la estructura real de datos
        sample_data = {
            'goles_local': [1],
            'goles_visitante': [0],
            'corners_local': [5],
            'corners_visitante': [3],
            'amarillas_local': [2],
            'amarillas_visitante': [1],
            'rojas_local': [0],
            'rojas_visitante': [0]
        }
        
        df = pd.DataFrame(sample_data)
        print(f"Sample data shape: {df.shape}")
        print(f"Sample data columns: {list(df.columns)}")
        
        # Intentar escalar
        features_scaled = scaler.transform(df.values)
        print(f"✓ Scaled features shape: {features_scaled.shape}")
        
        # Intentar predicción
        prediction = model.predict(features_scaled)
        print(f"✓ Prediction successful: {prediction}")
        print(f"Prediction type: {type(prediction)}")
        print(f"Prediction shape: {prediction.shape if hasattr(prediction, 'shape') else 'scalar'}")
        
    except Exception as e:
        print(f"✗ Error in model compatibility test: {e}")
        traceback.print_exc()

def main():
    """Función principal de diagnóstico"""
    print("=" * 50)
    print("DIAGNÓSTICO DE MODELOS DE PREDICCIÓN")
    print("=" * 50)
    print()
    
    check_python_version()
    check_dependencies()
    check_model_files()
    test_pickle_loading()
    test_with_different_encodings()
    test_model_compatibility()
    
    print("=" * 50)
    print("DIAGNÓSTICO COMPLETADO")
    print("=" * 50)

if __name__ == "__main__":
    main()
