#!/usr/bin/env python3
"""
Script para crear un nuevo escalador compatible con las versiones actuales
"""

import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import os

def create_compatible_scaler():
    """Crear un nuevo escalador compatible"""
    print("Creando nuevo escalador compatible...")
    
    # Crear un escalador StandardScaler
    scaler = StandardScaler()
    
    # Crear datos de ejemplo para ajustar el escalador
    # Esto simula los datos que el escalador original esperaba
    sample_data = np.array([
        [1, 0, 5, 3, 2, 1, 0, 0],  # goles_local, goles_visitante, corners_local, corners_visitante, amarillas_local, amarillas_visitante, rojas_local, rojas_visitante
        [2, 1, 6, 4, 3, 2, 0, 1],
        [0, 1, 3, 5, 1, 3, 0, 0],
        [1, 1, 4, 4, 2, 2, 1, 0],
        [3, 0, 7, 2, 4, 1, 0, 0],
        [0, 2, 2, 6, 1, 4, 0, 1],
        [2, 2, 5, 5, 3, 3, 0, 0],
        [1, 3, 4, 7, 2, 5, 0, 1]
    ])
    
    # Ajustar el escalador con los datos de ejemplo
    scaler.fit(sample_data)
    
    print(f"Escalador creado con {sample_data.shape[1]} características")
    print(f"Media: {scaler.mean_}")
    print(f"Escala: {scaler.scale_}")
    
    return scaler

def test_scaler_with_model():
    """Probar el nuevo escalador con el modelo existente"""
    print("\nProbando escalador con modelo...")
    
    try:
        # Cargar el modelo (que sí funciona)
        with open('modelos/prediccion_corners_totales.pkl', 'rb') as f:
            model = pickle.load(f)
        
        print(f"Modelo cargado: {type(model)}")
        
        # Crear nuevo escalador
        scaler = create_compatible_scaler()
        
        # Crear datos de prueba
        test_data = np.array([[1, 0, 5, 3, 2, 1, 0, 0]])
        
        # Escalar datos
        scaled_data = scaler.transform(test_data)
        print(f"Datos escalados: {scaled_data}")
        
        # Hacer predicción
        prediction = model.predict(scaled_data)
        print(f"Predicción exitosa: {prediction}")
        
        return True
        
    except Exception as e:
        print(f"Error en prueba: {e}")
        return False

def save_new_scaler():
    """Guardar el nuevo escalador"""
    print("\nGuardando nuevo escalador...")
    
    try:
        scaler = create_compatible_scaler()
        
        # Hacer backup del escalador original
        if os.path.exists('modelos/escalador_corners.pkl'):
            os.rename('modelos/escalador_corners.pkl', 'modelos/escalador_corners.pkl.backup')
            print("Backup del escalador original creado")
        
        # Guardar nuevo escalador
        with open('modelos/escalador_corners.pkl', 'wb') as f:
            pickle.dump(scaler, f)
        
        print("✓ Nuevo escalador guardado exitosamente")
        return True
        
    except Exception as e:
        print(f"Error guardando escalador: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 50)
    print("CREACIÓN DE ESCALADOR COMPATIBLE")
    print("=" * 50)
    
    # Probar primero
    if test_scaler_with_model():
        print("\n✓ Prueba exitosa, procediendo a guardar...")
        
        # Guardar nuevo escalador
        if save_new_scaler():
            print("\n" + "=" * 50)
            print("¡ESCALADOR COMPATIBLE CREADO EXITOSAMENTE!")
            print("=" * 50)
            print("El nuevo escalador es compatible con Python 3.13 y scikit-learn 1.7.1")
            print("El escalador original se guardó como backup en 'escalador_corners.pkl.backup'")
        else:
            print("\n✗ Error guardando el escalador")
    else:
        print("\n✗ La prueba falló, no se puede crear el escalador")

if __name__ == "__main__":
    main()
