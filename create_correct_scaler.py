#!/usr/bin/env python3
"""
Script para crear un escalador que solo maneje las 16 características numéricas
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

def create_numeric_scaler():
    """Crear un escalador solo para las características numéricas"""
    print("Creando escalador para características numéricas...")
    
    # Obtener datos de entrenamiento
    training_data = get_training_data()
    if not training_data:
        return None
    
    # Convertir a DataFrame
    df = pd.DataFrame(training_data)
    
    # Definir solo las características numéricas (sin los IDs)
    numeric_columns = [
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
    missing_columns = [col for col in numeric_columns if col not in df.columns]
    if missing_columns:
        print(f"❌ Columnas faltantes: {missing_columns}")
        return None
    
    print(f"✅ Todas las {len(numeric_columns)} columnas numéricas están disponibles")
    
    # Extraer características numéricas
    features = df[numeric_columns].values
    
    # Crear y ajustar escalador
    scaler = StandardScaler()
    scaler.fit(features)
    
    print(f"✅ Escalador creado con {scaler.n_features_in_} características numéricas")
    print(f"   Media: {scaler.mean_}")
    print(f"   Escala: {scaler.scale_}")
    
    return scaler

def test_complete_prediction():
    """Probar la predicción completa con escalador numérico + IDs"""
    print("\nProbando predicción completa...")
    
    try:
        # Crear escalador numérico
        scaler = create_numeric_scaler()
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
        
        # Características numéricas (16)
        numeric_columns = [
            'corners_vs_rival_hist', 'last3_vs_media_liga', 'local_avg_last3',
            'local_avg_last5', 'visitante_avg_last3', 'local_corner_category',
            'diff_last3_vs_last5_local', 'visitante_avg_last5', 'visitante_corner_category',
            'diff_last3_vs_last5_visitante', 'consistencia_corners_local',
            'tiros_bloqueados_local', 'corners_por_ataque_peligroso',
            'diff_corners_equipo', 'diff_corners_local', 'diff_corners_visitante'
        ]
        
        # IDs (2)
        id_columns = ['equipo_local_id', 'equipo_visitante_id']
        
        # Extraer características
        numeric_features = df[numeric_columns].values
        id_features = df[id_columns].values
        
        print(f"✅ Características numéricas: {numeric_features.shape}")
        print(f"✅ IDs: {id_features.shape}")
        
        # Escalar características numéricas
        features_scaled = scaler.transform(numeric_features)
        print(f"✅ Características escaladas: {features_scaled.shape}")
        
        # Crear array final con 18 características
        final_features = np.zeros((1, 18))
        final_features[0, :16] = features_scaled[0]  # 16 características escaladas
        final_features[0, 16] = id_features[0, 0]    # equipo_local_id
        final_features[0, 17] = id_features[0, 1]    # equipo_visitante_id
        
        print(f"✅ Características finales: {final_features.shape}")
        
        # Hacer predicción
        prediction = model.predict(final_features)
        print(f"✅ Predicción exitosa: {prediction[0]}")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False

def save_numeric_scaler():
    """Guardar el escalador numérico"""
    print("\nGuardando escalador numérico...")
    
    try:
        scaler = create_numeric_scaler()
        if not scaler:
            return False
        
        # Backup del escalador original
        if os.path.exists('modelos/escalador_corners.pkl'):
            os.rename('modelos/escalador_corners.pkl', 'modelos/escalador_corners.pkl.backup3')
            print("✅ Backup del escalador original creado")
        
        # Guardar nuevo escalador
        with open('modelos/escalador_corners.pkl', 'wb') as f:
            pickle.dump(scaler, f)
        
        print("✅ Nuevo escalador numérico guardado exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error guardando escalador: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("CREACIÓN DE ESCALADOR NUMÉRICO")
    print("=" * 60)
    
    # Probar primero
    if test_complete_prediction():
        print("\n✅ Prueba exitosa, procediendo a guardar...")
        
        # Guardar nuevo escalador
        if save_numeric_scaler():
            print("\n" + "=" * 60)
            print("¡ESCALADOR NUMÉRICO CREADO EXITOSAMENTE!")
            print("=" * 60)
            print("El escalador maneja solo las 16 características numéricas")
            print("Los IDs se agregan sin escalar para completar las 18 características")
        else:
            print("\n❌ Error guardando el escalador")
    else:
        print("\n❌ La prueba falló, no se puede crear el escalador")

if __name__ == "__main__":
    main()
