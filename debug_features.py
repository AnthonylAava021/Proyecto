#!/usr/bin/env python3
"""
Script para debuggear las características disponibles vs las esperadas
"""

import psycopg2
import psycopg2.extras
import pickle
import numpy as np
import pandas as pd

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'user',
    'password': 'ups_bet05',
    'database': 'UPS_BET',
    'port': 5432
}

def get_sample_data():
    """Obtener datos de muestra de la base de datos"""
    print("Obteniendo datos de muestra...")
    
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM corners_tabla 
                WHERE equipo_local_id = 4 AND equipo_visitante_id = 0 
                ORDER BY fecha DESC 
                LIMIT 1
            """)
            result = cursor.fetchone()
            
            if result:
                print("✅ Datos obtenidos de la base de datos")
                return dict(result)
            else:
                print("❌ No se encontraron datos")
                return None
                
    except Exception as e:
        print(f"❌ Error obteniendo datos: {e}")
        return None
    finally:
        connection.close()

def analyze_features():
    """Analizar las características disponibles vs esperadas"""
    print("=" * 60)
    print("ANÁLISIS DE CARACTERÍSTICAS")
    print("=" * 60)
    
    # Obtener datos de muestra
    sample_data = get_sample_data()
    if not sample_data:
        return
    
    print(f"\n📊 Datos de muestra (fecha: {sample_data.get('fecha', 'N/A')}):")
    print(f"   Equipo local: {sample_data.get('equipo_local_id')}")
    print(f"   Equipo visitante: {sample_data.get('equipo_visitante_id')}")
    
    # Cargar escalador para ver qué espera
    print("\n🔍 Cargando escalador...")
    try:
        with open('modelos/escalador_corners.pkl', 'rb') as f:
            scaler = pickle.load(f)
        
        print(f"✅ Escalador cargado: {type(scaler)}")
        print(f"   Características esperadas: {scaler.n_features_in_}")
        
        if hasattr(scaler, 'feature_names_in_'):
            print(f"   Nombres esperados: {list(scaler.feature_names_in_)}")
        
    except Exception as e:
        print(f"❌ Error cargando escalador: {e}")
        return
    
    # Analizar datos disponibles
    print(f"\n📋 Características disponibles en la base de datos:")
    exclude_columns = ['fecha', 'equipo_local_id', 'equipo_visitante_id', 'id']
    
    available_features = []
    for key, value in sample_data.items():
        if key not in exclude_columns:
            available_features.append(key)
            print(f"   - {key}: {value} ({type(value).__name__})")
    
    print(f"\n📈 Resumen:")
    print(f"   Características disponibles: {len(available_features)}")
    print(f"   Características esperadas: {scaler.n_features_in_}")
    print(f"   Diferencia: {scaler.n_features_in_ - len(available_features)}")
    
    # Intentar preparar características
    print(f"\n🔧 Intentando preparar características...")
    try:
        df = pd.DataFrame([sample_data])
        exclude_columns = ['fecha', 'equipo_local_id', 'equipo_visitante_id', 'id']
        feature_columns = [col for col in df.columns if col not in exclude_columns]
        
        print(f"   Columnas de características: {feature_columns}")
        print(f"   Número de características: {len(feature_columns)}")
        
        features = df[feature_columns].values
        print(f"   Shape de características: {features.shape}")
        
        # Intentar escalar
        features_scaled = scaler.transform(features)
        print(f"✅ Escalado exitoso: {features_scaled.shape}")
        
        # Cargar modelo y predecir
        print(f"\n🤖 Cargando modelo...")
        with open('modelos/prediccion_corners_totales.pkl', 'rb') as f:
            model = pickle.load(f)
        
        prediction = model.predict(features_scaled)
        print(f"✅ Predicción exitosa: {prediction[0]}")
        
    except Exception as e:
        print(f"❌ Error en preparación: {e}")
        print(f"   Tipo de error: {type(e)}")

def main():
    """Función principal"""
    analyze_features()

if __name__ == "__main__":
    main()
