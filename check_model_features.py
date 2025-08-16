#!/usr/bin/env python3
"""
Script para verificar exactamente qué características espera el modelo
"""

import pickle
import numpy as np

def check_model_features():
    """Verificar las características que espera el modelo"""
    print("=" * 60)
    print("VERIFICACIÓN DE CARACTERÍSTICAS DEL MODELO")
    print("=" * 60)
    
    try:
        # Cargar modelo
        with open('modelos/prediccion_corners_totales.pkl', 'rb') as f:
            model = pickle.load(f)
        
        print(f"✅ Modelo cargado: {type(model)}")
        
        # Verificar características esperadas
        if hasattr(model, 'n_features_in_'):
            print(f"📊 Características esperadas por el modelo: {model.n_features_in_}")
        
        if hasattr(model, 'feature_names_in_'):
            print(f"📋 Nombres de características esperadas:")
            for i, name in enumerate(model.feature_names_in_):
                print(f"   {i+1:2d}. {name}")
        
        # Intentar diferentes tamaños para encontrar el correcto
        print(f"\n🔍 Probando diferentes tamaños de características...")
        for n_features in [16, 17, 18, 19, 20]:
            try:
                test_data = np.random.random((1, n_features))
                prediction = model.predict(test_data)
                print(f"✅ Modelo acepta {n_features} características - Predicción: {prediction[0]:.2f}")
                break
            except Exception as e:
                print(f"❌ {n_features} características falló: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando modelo: {e}")
        return False

def main():
    """Función principal"""
    check_model_features()

if __name__ == "__main__":
    main()
