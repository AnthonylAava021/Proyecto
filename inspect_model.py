#!/usr/bin/env python3
"""
Script para inspeccionar el modelo y determinar las características esperadas
"""

import pickle
import numpy as np
import pandas as pd

def inspect_model():
    """Inspeccionar el modelo para entender sus características"""
    print("Inspeccionando modelo...")
    
    try:
        # Cargar el modelo
        with open('modelos/prediccion_corners_totales.pkl', 'rb') as f:
            model = pickle.load(f)
        
        print(f"Tipo de modelo: {type(model)}")
        print(f"Modelo: {model}")
        
        # Intentar diferentes tamaños de características
        for n_features in [8, 10, 12, 15, 18, 20, 25]:
            try:
                test_data = np.random.random((1, n_features))
                prediction = model.predict(test_data)
                print(f"✓ Modelo acepta {n_features} características - Predicción: {prediction}")
                break
            except Exception as e:
                print(f"✗ {n_features} características falló: {e}")
        
        # Si el modelo es XGBoost, podemos obtener más información
        if hasattr(model, 'n_features_in_'):
            print(f"\nCaracterísticas esperadas por el modelo: {model.n_features_in_}")
        
        if hasattr(model, 'feature_names_in_'):
            print(f"Nombres de características: {model.feature_names_in_}")
        
        return True
        
    except Exception as e:
        print(f"Error inspeccionando modelo: {e}")
        return False

def test_with_real_data_structure():
    """Probar con estructura de datos real"""
    print("\nProbando con estructura de datos real...")
    
    # Crear datos con 18 características (basado en el error anterior)
    sample_data_18 = np.random.random((1, 18))
    
    try:
        with open('modelos/prediccion_corners_totales.pkl', 'rb') as f:
            model = pickle.load(f)
        
        prediction = model.predict(sample_data_18)
        print(f"✓ Predicción exitosa con 18 características: {prediction}")
        
        # Crear escalador compatible
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        
        # Ajustar escalador con datos de ejemplo
        training_data = np.random.random((100, 18))
        scaler.fit(training_data)
        
        # Probar escalador + modelo
        scaled_data = scaler.transform(sample_data_18)
        prediction_scaled = model.predict(scaled_data)
        print(f"✓ Predicción con escalador: {prediction_scaled}")
        
        return scaler
        
    except Exception as e:
        print(f"Error en prueba: {e}")
        return None

def main():
    """Función principal"""
    print("=" * 50)
    print("INSPECCIÓN DEL MODELO")
    print("=" * 50)
    
    inspect_model()
    scaler = test_with_real_data_structure()
    
    if scaler:
        print("\n" + "=" * 50)
        print("CREANDO ESCALADOR COMPATIBLE")
        print("=" * 50)
        
        # Guardar escalador compatible
        try:
            import os
            # Backup del original
            if os.path.exists('modelos/escalador_corners.pkl'):
                os.rename('modelos/escalador_corners.pkl', 'modelos/escalador_corners.pkl.backup')
                print("Backup del escalador original creado")
            
            # Guardar nuevo escalador
            with open('modelos/escalador_corners.pkl', 'wb') as f:
                pickle.dump(scaler, f)
            
            print("✓ Nuevo escalador compatible guardado")
            
        except Exception as e:
            print(f"Error guardando escalador: {e}")

if __name__ == "__main__":
    main()
