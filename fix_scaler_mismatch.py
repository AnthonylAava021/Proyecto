#!/usr/bin/env python3
"""
Script para crear un escalador que coincida con las características reales de la base de datos
"""

import psycopg2
import psycopg2.extras
import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import os

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'user',
    'password': 'ups_bet05',
    'database': 'UPS_BET',
    'port': 5432
}

def get_training_data():
    """Obtener datos de entrenamiento de la base de datos"""
    print("Obteniendo datos de entrenamiento...")
    
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM corners_tabla 
                ORDER BY fecha DESC 
                LIMIT 100
            """)
            results = cursor.fetchall()
            
            if results:
                print(f"✅ Obtenidos {len(results)} registros de entrenamiento")
                return [dict(row) for row in results]
            else:
                print("❌ No se encontraron datos")
                return None
                
    except Exception as e:
        print(f"❌ Error obteniendo datos: {e}")
        return None
    finally:
        connection.close()

def create_compatible_scaler():
    """Crear un escalador compatible con los datos reales"""
    print("Creando escalador compatible...")
    
    # Obtener datos de entrenamiento
    training_data = get_training_data()
    if not training_data:
        return None
    
    # Convertir a DataFrame
    df = pd.DataFrame(training_data)
    
    # Definir columnas de características (basado en el análisis anterior)
    feature_columns = [
        'corners_vs_rival_hist',
        'last3_vs_media_liga',
        'local_avg_last3',
        'local_avg_last5',
        'visitante_avg_last3',
        'local_corner_category',
        'diff_last3_vs_last5_local',
        'visitante_avg_last5',
        'visitante_corner_category',
        'diff_last3_vs_last5_visitante',
        'consistencia_corners_local',
        'tiros_bloqueados_local',
        'corners_por_ataque_peligroso',
        'diff_corners_equipo',
        'diff_corners_local',
        'diff_corners_visitante'
    ]
    
    # Verificar que todas las columnas existen
    missing_columns = [col for col in feature_columns if col not in df.columns]
    if missing_columns:
        print(f"❌ Columnas faltantes: {missing_columns}")
        return None
    
    print(f"✅ Todas las {len(feature_columns)} columnas están disponibles")
    
    # Extraer características
    features = df[feature_columns].values
    
    # Crear y ajustar escalador
    scaler = StandardScaler()
    scaler.fit(features)
    
    print(f"✅ Escalador creado con {scaler.n_features_in_} características")
    print(f"   Media: {scaler.mean_}")
    print(f"   Escala: {scaler.scale_}")
    
    return scaler

def test_new_scaler():
    """Probar el nuevo escalador con el modelo"""
    print("\nProbando nuevo escalador...")
    
    try:
        # Crear escalador compatible
        scaler = create_compatible_scaler()
        if not scaler:
            return False
        
        # Cargar modelo
        with open('modelos/prediccion_corners_totales.pkl', 'rb') as f:
            model = pickle.load(f)
        
        print(f"✅ Modelo cargado: {type(model)}")
        
        # Obtener datos de prueba
        connection = psycopg2.connect(**DB_CONFIG)
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM corners_tabla 
                WHERE equipo_local_id = 4 AND equipo_visitante_id = 0 
                ORDER BY fecha DESC 
                LIMIT 1
            """)
            test_data = cursor.fetchone()
        connection.close()
        
        if not test_data:
            print("❌ No se encontraron datos de prueba")
            return False
        
        # Preparar características
        df = pd.DataFrame([dict(test_data)])
        feature_columns = [
            'corners_vs_rival_hist', 'last3_vs_media_liga', 'local_avg_last3',
            'local_avg_last5', 'visitante_avg_last3', 'local_corner_category',
            'diff_last3_vs_last5_local', 'visitante_avg_last5', 'visitante_corner_category',
            'diff_last3_vs_last5_visitante', 'consistencia_corners_local',
            'tiros_bloqueados_local', 'corners_por_ataque_peligroso',
            'diff_corners_equipo', 'diff_corners_local', 'diff_corners_visitante'
        ]
        
        features = df[feature_columns].values
        print(f"✅ Características preparadas: {features.shape}")
        
        # Escalar y predecir
        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)
        
        print(f"✅ Predicción exitosa: {prediction[0]}")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False

def save_new_scaler():
    """Guardar el nuevo escalador"""
    print("\nGuardando nuevo escalador...")
    
    try:
        scaler = create_compatible_scaler()
        if not scaler:
            return False
        
        # Backup del escalador original
        if os.path.exists('modelos/escalador_corners.pkl'):
            os.rename('modelos/escalador_corners.pkl', 'modelos/escalador_corners.pkl.backup2')
            print("✅ Backup del escalador original creado")
        
        # Guardar nuevo escalador
        with open('modelos/escalador_corners.pkl', 'wb') as f:
            pickle.dump(scaler, f)
        
        print("✅ Nuevo escalador guardado exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error guardando escalador: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("CREACIÓN DE ESCALADOR COMPATIBLE CON DATOS REALES")
    print("=" * 60)
    
    # Probar primero
    if test_new_scaler():
        print("\n✅ Prueba exitosa, procediendo a guardar...")
        
        # Guardar nuevo escalador
        if save_new_scaler():
            print("\n" + "=" * 60)
            print("¡ESCALADOR COMPATIBLE CREADO EXITOSAMENTE!")
            print("=" * 60)
            print("El nuevo escalador coincide con las 16 características reales")
            print("de la base de datos y es compatible con el modelo.")
        else:
            print("\n❌ Error guardando el escalador")
    else:
        print("\n❌ La prueba falló, no se puede crear el escalador")

if __name__ == "__main__":
    main()
