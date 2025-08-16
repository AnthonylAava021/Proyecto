#!/usr/bin/env python3
"""
Script para verificar el modelo de predicción
"""

import pickle
import os

def check_model():
    print("=" * 60)
    print("VERIFICACIÓN DEL MODELO")
    print("=" * 60)
    
    model_path = "modelos/modelo_ligapro.pkl"
    
    # Verificar si existe el archivo
    if not os.path.exists(model_path):
        print(f"❌ El archivo {model_path} no existe")
        return False
    
    print(f"✅ Archivo encontrado: {model_path}")
    print(f"   Tamaño: {os.path.getsize(model_path)} bytes")
    
    # Intentar cargar el modelo
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        print(f"✅ Modelo cargado exitosamente")
        print(f"   Tipo: {type(model)}")
        
        # Verificar propiedades del modelo
        if hasattr(model, 'n_features_in_'):
            print(f"   Características esperadas: {model.n_features_in_}")
        
        if hasattr(model, 'feature_names_in_'):
            print(f"   Nombres de características: {model.feature_names_in_}")
        
        # Probar predicción con datos dummy
        try:
            # Crear datos de prueba (ajustar según las características esperadas)
            import numpy as np
            
            # Intentar con diferentes números de características
            for n_features in [10, 12, 15, 18, 20]:
                try:
                    test_data = np.random.random((1, n_features))
                    prediction = model.predict(test_data)
                    print(f"✅ Predicción exitosa con {n_features} características")
                    print(f"   Resultado: {prediction}")
                    print(f"   Forma: {prediction.shape}")
                    break
                except Exception as e:
                    print(f"❌ Error con {n_features} características: {e}")
                    continue
            
        except Exception as e:
            print(f"❌ Error en predicción de prueba: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error cargando modelo: {e}")
        print(f"   Tipo de error: {type(e)}")
        return False

if __name__ == "__main__":
    check_model()


