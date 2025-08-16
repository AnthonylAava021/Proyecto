from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import pickle
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__, static_folder='public')
CORS(app)

# Configuración de la base de datos PostgreSQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'user',
    'password': 'ups_bet05',
    'database': 'UPS_BET',
    'port': 5432
}

# Cargar modelos
def load_models():
    try:
        print("=" * 50)
        print("CARGANDO MODELOS DE MACHINE LEARNING")
        print("=" * 50)
        
        # Cargar modelo de resultados
        print("📊 Cargando modelo de predicción de resultados...")
        modelo_dict = joblib.load('modelos/modelo_ligapro.pkl')
        model_resultados = modelo_dict  # Guardamos todo el diccionario
        print(f"✅ Modelo de resultados cargado: {type(modelo_dict).__name__}")
        print(f"✅ Contiene: {list(modelo_dict.keys())}")
        
        # Cargar modelo de corners
        print("⚽ Cargando modelo de predicción de corners...")
        with open('modelos/prediccion_corners_totales.pkl', 'rb') as f:
            model_corners = pickle.load(f)
        print(f"✅ Modelo de corners cargado: {type(model_corners).__name__}")
        
        # Cargar escalador de corners
        print("🔧 Cargando escalador de datos...")
        with open('modelos/escalador_corners.pkl', 'rb') as f:
            scaler_corners = pickle.load(f)
        print(f"✅ Escalador cargado: {type(scaler_corners).__name__}")
        
        print("=" * 50)
        print("🎯 TODOS LOS MODELOS CARGADOS EXITOSAMENTE")
        print("=" * 50)
        
        return model_resultados, model_corners, scaler_corners
    except Exception as e:
        print(f"❌ Error cargando modelos: {e}")
        print(f"❌ Tipo de error: {type(e)}")
        return None, None, None

model_resultados, model_corners, scaler_corners = load_models()

def get_db_connection():
    """Crear conexión a la base de datos PostgreSQL"""
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        print(f"Tipo de error: {type(e)}")
        return None

def get_historical_data(fecha_corte=None):
    """
    Obtener todos los datos históricos hasta la fecha de corte
    """
    if fecha_corte is None:
        # Si no se especifica fecha, usar hoy a las 00:00
        fecha_corte = datetime.now().strftime('%Y-%m-%d')
    
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            sql = """
            SELECT * FROM ganador_resultado_tabla 
            WHERE fecha < %s 
            ORDER BY fecha DESC
            """
            cursor.execute(sql, (fecha_corte,))
            results = cursor.fetchall()
            
            if results:
                return [dict(row) for row in results]
            return []
            
    except Exception as e:
        print(f"Error en consulta de base de datos: {e}")
        return None
    finally:
        connection.close()

def get_average_result_data(equipo_local_id, equipo_visitante_id, fecha_corte=None):
    """
    Obtener el promedio de todos los registros de un enfrentamiento específico en ganador_resultado_tabla
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            # Construir la consulta con filtro de fecha si se proporciona
            fecha_filter = ""
            params = [equipo_local_id, equipo_visitante_id]
            
            if fecha_corte:
                fecha_filter = "AND fecha < %s"
                params.append(fecha_corte)
            
            # Buscar enfrentamiento directo y calcular promedios
            sql = f"""
            SELECT 
                AVG(ataques_visitante) as ataques_visitante,
                AVG(intentos_a_porteria_local) as intentos_a_porteria_local,
                AVG(fuera_de_juego_local) as fuera_de_juego_local,
                AVG(posesion_local) as posesion_local,
                AVG(corners_visitante) as corners_visitante,
                AVG(corners_local) as corners_local,
                AVG(tarjetas_amarillas_totales) as tarjetas_amarillas_totales,
                AVG(ataques_peligrosos_local) as ataques_peligrosos_local,
                AVG(ataques_local) as ataques_local,
                AVG(faltas_local) as faltas_local,
                AVG(posesion_visitante) as posesion_visitante,
                AVG(atajadas_visitante) as atajadas_visitante,
                AVG(intentos_a_porteria_visitante) as intentos_a_porteria_visitante,
                AVG(tiros_fuera_visitante) as tiros_fuera_visitante,
                AVG(tarjetas_rojas_visitante) as tarjetas_rojas_visitante,
                AVG(ataques_peligrosos_visitante) as ataques_peligrosos_visitante,
                AVG(tarjetas_rojas_totales) as tarjetas_rojas_totales,
                AVG(tarjetas_rojas_local) as tarjetas_rojas_local,
                AVG(tarjetas_amarillas_local) as tarjetas_amarillas_local,
                AVG(faltas_visitante) as faltas_visitante,
                AVG(faltas_totales) as faltas_totales,
                AVG(tiros_fuera_local) as tiros_fuera_local,
                AVG(tarjetas_totales) as tarjetas_totales,
                AVG(tarjetas_amarillas_visitante) as tarjetas_amarillas_visitante,
                AVG(tiros_esquina_totales) as tiros_esquina_totales,
                AVG(penales_visitante) as penales_visitante,
                AVG(tiros_a_puerta_visitante) as tiros_a_puerta_visitante,
                AVG(tiros_bloqueados_visitante) as tiros_bloqueados_visitante,
                AVG(tiros_a_puerta_local) as tiros_a_puerta_local,
                AVG(fuera_de_juego_visitante) as fuera_de_juego_visitante,
                AVG(tiros_bloqueados_local) as tiros_bloqueados_local,
                AVG(atajadas_local) as atajadas_local,
                AVG(penales_local) as penales_local,
                COUNT(*) as num_partidos
            FROM ganador_resultado_tabla 
            WHERE equipo_local_id = %s AND equipo_visitante_id = %s {fecha_filter}
            """
            cursor.execute(sql, params)
            result = cursor.fetchone()
            
            if result and result['num_partidos'] > 0:
                print(f"📊 Encontrados {result['num_partidos']} partidos directos (resultados)")
                return dict(result)
            
            # Si no existe, buscar enfrentamiento inverso y calcular promedios
            params = [equipo_visitante_id, equipo_local_id]
            if fecha_corte:
                params.append(fecha_corte)
            
            sql = f"""
            SELECT 
                AVG(ataques_visitante) as ataques_visitante,
                AVG(intentos_a_porteria_local) as intentos_a_porteria_local,
                AVG(fuera_de_juego_local) as fuera_de_juego_local,
                AVG(posesion_local) as posesion_local,
                AVG(corners_visitante) as corners_visitante,
                AVG(corners_local) as corners_local,
                AVG(tarjetas_amarillas_totales) as tarjetas_amarillas_totales,
                AVG(ataques_peligrosos_local) as ataques_peligrosos_local,
                AVG(ataques_local) as ataques_local,
                AVG(faltas_local) as faltas_local,
                AVG(posesion_visitante) as posesion_visitante,
                AVG(atajadas_visitante) as atajadas_visitante,
                AVG(intentos_a_porteria_visitante) as intentos_a_porteria_visitante,
                AVG(tiros_fuera_visitante) as tiros_fuera_visitante,
                AVG(tarjetas_rojas_visitante) as tarjetas_rojas_visitante,
                AVG(ataques_peligrosos_visitante) as ataques_peligrosos_visitante,
                AVG(tarjetas_rojas_totales) as tarjetas_rojas_totales,
                AVG(tarjetas_rojas_local) as tarjetas_rojas_local,
                AVG(tarjetas_amarillas_local) as tarjetas_amarillas_local,
                AVG(faltas_visitante) as faltas_visitante,
                AVG(faltas_totales) as faltas_totales,
                AVG(tiros_fuera_local) as tiros_fuera_local,
                AVG(tarjetas_totales) as tarjetas_totales,
                AVG(tarjetas_amarillas_visitante) as tarjetas_amarillas_visitante,
                AVG(tiros_esquina_totales) as tiros_esquina_totales,
                AVG(penales_visitante) as penales_visitante,
                AVG(tiros_a_puerta_visitante) as tiros_a_puerta_visitante,
                AVG(tiros_bloqueados_visitante) as tiros_bloqueados_visitante,
                AVG(tiros_a_puerta_local) as tiros_a_puerta_local,
                AVG(fuera_de_juego_visitante) as fuera_de_juego_visitante,
                AVG(tiros_bloqueados_local) as tiros_bloqueados_local,
                AVG(atajadas_local) as atajadas_local,
                AVG(penales_local) as penales_local,
                COUNT(*) as num_partidos
            FROM ganador_resultado_tabla 
            WHERE equipo_local_id = %s AND equipo_visitante_id = %s {fecha_filter}
            """
            cursor.execute(sql, params)
            result = cursor.fetchone()
            
            if result and result['num_partidos'] > 0:
                print(f"📊 Encontrados {result['num_partidos']} partidos inversos (resultados)")
                return dict(result)
            
            print("❌ No se encontraron partidos históricos para este enfrentamiento (resultados)")
            return None
            
    except Exception as e:
        print(f"Error en consulta de resultados: {e}")
        return None
    finally:
        connection.close()

def get_team_stats(df_corte, equipo_id, is_local=True):
    """
    Calcular estadísticas de un equipo basado en datos históricos
    """
    if df_corte.empty:
        return {}
    
    # Filtrar partidos del equipo
    if is_local:
        team_matches = df_corte[df_corte['equipo_local_id'] == equipo_id]
    else:
        team_matches = df_corte[df_corte['equipo_visitante_id'] == equipo_id]
    
    if team_matches.empty:
        # Si no hay datos, usar medias globales
        return {
            'goles_promedio': df_corte['goles_local'].mean() if is_local else df_corte['goles_visitante'].mean(),
            'partidos_jugados': 0,
            'victorias': 0,
            'empates': 0,
            'derrotas': 0
        }
    
    # Calcular estadísticas
    if is_local:
        goles = team_matches['goles_local']
        goles_recibidos = team_matches['goles_visitante']
    else:
        goles = team_matches['goles_visitante']
        goles_recibidos = team_matches['goles_local']
    
    stats = {
        'goles_promedio': goles.mean(),
        'goles_recibidos_promedio': goles_recibidos.mean(),
        'partidos_jugados': len(team_matches),
        'victorias': len(team_matches[goles > goles_recibidos]),
        'empates': len(team_matches[goles == goles_recibidos]),
        'derrotas': len(team_matches[goles < goles_recibidos])
    }
    
    return stats

def prepare_features(equipo_local_id, equipo_visitante_id, fecha_corte=None):
    """
    Preparar características para el modelo de predicción de resultados usando promedios
    """
    # Obtener datos promedio del enfrentamiento específico
    match_data = get_average_result_data(equipo_local_id, equipo_visitante_id, fecha_corte)
    
    if not match_data:
        return None, None
    
    # Obtener las características esperadas del modelo
    expected_features = model_resultados['feature_columns'].tolist()
    
    # Crear características para el modelo usando los promedios reales
    features = {}
    for feature in expected_features:
        if feature == 'equipo_local_id':
            features[feature] = equipo_local_id
        elif feature == 'equipo_visitante_id':
            features[feature] = equipo_visitante_id
        else:
            # Usar los valores promedio reales de la base de datos
            if feature in match_data and match_data[feature] is not None:
                features[feature] = float(match_data[feature])
            else:
                # Valor por defecto si no existe
                features[feature] = 5.0
    
    features_array = np.array([[features[col] for col in expected_features]])
    
    print(f"🔢 Características extraídas: {len(expected_features)} features")
    print(f"📋 Features disponibles: {expected_features}")
    
    return features_array, expected_features
    
    return features_array, expected_features

def predict_match_result(equipo_local_id, equipo_visitante_id, fecha_corte=None):
    """
    Predecir resultado de un partido
    """
    # Verificar que el modelo esté cargado
    if model_resultados is None:
        return {
            'error': '❌ El modelo de predicción de resultados no está disponible. Verifica que el archivo modelo_ligapro.pkl existe y es válido.',
            'goles_local': None,
            'goles_visitante': None,
            'resultado_1x2': None
        }
    
    # Validar que no sean el mismo equipo
    if equipo_local_id == equipo_visitante_id:
        return {
            'error': 'No se puede predecir un partido entre el mismo equipo',
            'goles_local': None,
            'goles_visitante': None,
            'resultado_1x2': None
        }
    
    # Preparar características
    features, feature_columns = prepare_features(equipo_local_id, equipo_visitante_id, fecha_corte)
    
    if features is None:
        return {
            'error': 'Error preparando características para el modelo (promedio de partidos)',
            'goles_local': None,
            'goles_visitante': None,
            'resultado_1x2': None
        }
    
    try:
        # Hacer predicción usando los modelos separados
        model_gl = model_resultados['model_gl']
        model_gv = model_resultados['model_gv']
        
        print("=" * 60)
        print("🎯 REALIZANDO PREDICCIÓN DE RESULTADO")
        print("=" * 60)
        print(f"📊 Modelo Local (goles): {type(model_gl).__name__}")
        print(f"📊 Modelo Visitante (goles): {type(model_gv).__name__}")
        print(f"🔢 Características enviadas: {features.shape[1]} features")
        print(f"📋 Features: {feature_columns}")
        print("-" * 60)
        
        # Predecir goles local y visitante por separado
        print("⚽ Prediciendo goles local...")
        goles_local_raw = float(model_gl.predict(features)[0])
        print(f"✅ Goles local (raw): {goles_local_raw:.4f}")
        
        print("⚽ Prediciendo goles visitante...")
        goles_visitante_raw = float(model_gv.predict(features)[0])
        print(f"✅ Goles visitante (raw): {goles_visitante_raw:.4f}")
        
        print("-" * 60)
        print(f"🎯 Predicción final: {round(goles_local_raw)} - {round(goles_visitante_raw)}")
        print("=" * 60)
        
        # Redondear para obtener marcador entero
        goles_local_rounded = round(goles_local_raw)
        goles_visitante_rounded = round(goles_visitante_raw)
        
        # Determinar resultado 1X2
        if goles_local_rounded > goles_visitante_rounded:
            resultado_1x2 = 1  # Victoria local
        elif goles_local_rounded < goles_visitante_rounded:
            resultado_1x2 = 2  # Victoria visitante
        else:
            resultado_1x2 = 0  # Empate
        
        return {
            'goles_local': {
                'raw': goles_local_raw,
                'rounded': goles_local_rounded
            },
            'goles_visitante': {
                'raw': goles_visitante_raw,
                'rounded': goles_visitante_rounded
            },
            'resultado_1x2': resultado_1x2,
            'features_used': feature_columns
        }
        
    except Exception as e:
        return {
            'error': f'Error en predicción: {str(e)}',
            'goles_local': None,
            'goles_visitante': None,
            'resultado_1x2': None
        }

def get_average_match_data(equipo_local_id, equipo_visitante_id):
    """
    Obtener el promedio de todos los registros de un enfrentamiento específico
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            # Buscar enfrentamiento directo y calcular promedios
            sql = """
            SELECT 
                AVG(consistencia_corners_local) as consistencia_corners_local,
                AVG(corners_por_ataque_peligroso) as corners_por_ataque_peligroso,
                AVG(corners_vs_rival_hist) as corners_vs_rival_hist,
                AVG(diff_corners_equipo) as diff_corners_equipo,
                AVG(diff_corners_local) as diff_corners_local,
                AVG(diff_corners_visitante) as diff_corners_visitante,
                AVG(local_avg_last3) as local_avg_last3,
                AVG(local_avg_last5) as local_avg_last5,
                AVG(visitante_avg_last3) as visitante_avg_last3,
                AVG(visitante_avg_last5) as visitante_avg_last5,
                AVG(local_corner_category) as local_corner_category,
                AVG(visitante_corner_category) as visitante_corner_category,
                AVG(diff_last3_vs_last5_local) as diff_last3_vs_last5_local,
                AVG(diff_last3_vs_last5_visitante) as diff_last3_vs_last5_visitante,
                AVG(tiros_bloqueados_local) as tiros_bloqueados_local,
                AVG(last3_vs_media_liga) as last3_vs_media_liga,
                COUNT(*) as num_partidos
            FROM corners_tabla 
            WHERE equipo_local_id = %s AND equipo_visitante_id = %s
            """
            cursor.execute(sql, (equipo_local_id, equipo_visitante_id))
            result = cursor.fetchone()
            
            if result and result['num_partidos'] > 0:
                print(f"📊 Encontrados {result['num_partidos']} partidos directos")
                return dict(result)
            
            # Si no existe, buscar enfrentamiento inverso y calcular promedios
            sql = """
            SELECT 
                AVG(consistencia_corners_local) as consistencia_corners_local,
                AVG(corners_por_ataque_peligroso) as corners_por_ataque_peligroso,
                AVG(corners_vs_rival_hist) as corners_vs_rival_hist,
                AVG(diff_corners_equipo) as diff_corners_equipo,
                AVG(diff_corners_local) as diff_corners_local,
                AVG(diff_corners_visitante) as diff_corners_visitante,
                AVG(local_avg_last3) as local_avg_last3,
                AVG(local_avg_last5) as local_avg_last5,
                AVG(visitante_avg_last3) as visitante_avg_last3,
                AVG(visitante_avg_last5) as visitante_avg_last5,
                AVG(local_corner_category) as local_corner_category,
                AVG(visitante_corner_category) as visitante_corner_category,
                AVG(diff_last3_vs_last5_local) as diff_last3_vs_last5_local,
                AVG(diff_last3_vs_last5_visitante) as diff_last3_vs_last5_visitante,
                AVG(tiros_bloqueados_local) as tiros_bloqueados_local,
                AVG(last3_vs_media_liga) as last3_vs_media_liga,
                COUNT(*) as num_partidos
            FROM corners_tabla 
            WHERE equipo_local_id = %s AND equipo_visitante_id = %s
            """
            cursor.execute(sql, (equipo_visitante_id, equipo_local_id))
            result = cursor.fetchone()
            
            if result and result['num_partidos'] > 0:
                print(f"📊 Encontrados {result['num_partidos']} partidos inversos")
                return dict(result)
            
            print("❌ No se encontraron partidos históricos para este enfrentamiento")
            return None
            
    except Exception as e:
        print(f"Error en consulta de corners: {e}")
        return None
    finally:
        connection.close()

def prepare_corners_features(match_data):
    """
    Preparar características para el modelo de corners
    """
    if not match_data:
        return None, None
    
    # Columnas que realmente existen en la base de datos
    expected_columns = [
        'consistencia_corners_local',
        'corners_por_ataque_peligroso',
        'corners_vs_rival_hist',
        'diff_corners_equipo',
        'diff_corners_local',
        'diff_corners_visitante',
        'local_avg_last3',
        'local_avg_last5',
        'visitante_avg_last3',
        'visitante_avg_last5',
        'local_corner_category',
        'visitante_corner_category',
        'diff_last3_vs_last5_local',
        'diff_last3_vs_last5_visitante',
        'tiros_bloqueados_local',
        'last3_vs_media_liga'
    ]
    
    # Extraer características específicas
    features = {}
    for col in expected_columns:
        if col in match_data and match_data[col] is not None:
            features[col] = float(match_data[col])
        else:
            # Valor por defecto si no existe
            features[col] = 0.0
    
    # Ordenar características para mantener consistencia
    feature_columns = sorted(features.keys())
    features_array = np.array([[features[col] for col in feature_columns]])
    
    print(f"🔢 Características extraídas: {len(feature_columns)} features")
    print(f"📋 Features disponibles: {feature_columns}")
    
    return features_array, feature_columns

def predict_corners(equipo_local_id, equipo_visitante_id):
    """
    Predecir corners totales del partido
    """
    # Verificar que los modelos estén cargados
    if model_corners is None or scaler_corners is None:
        return {
            'error': '❌ Los modelos de corners no están disponibles. Verifica que los archivos prediccion_corners_totales.pkl y escalador_corners.pkl existen y son válidos.',
            'corners_totales': None
        }
    
    # Verificar que no sean el mismo equipo
    if equipo_local_id == equipo_visitante_id:
        return {
            'error': 'Los equipos local y visitante no pueden ser iguales',
            'corners_totales': None
        }
    
    # Obtener datos promedio del enfrentamiento
    match_data = get_average_match_data(equipo_local_id, equipo_visitante_id)
    
    if not match_data:
        return {
            'error': 'No se encontraron datos históricos para este enfrentamiento (promedio de partidos)',
            'corners_totales': None
        }
    
    # Preparar características
    features, feature_columns = prepare_corners_features(match_data)
    
    if features is None:
        return {
            'error': 'Error preparando características para el modelo de corners',
            'corners_totales': None
        }
    
    try:
        print("=" * 60)
        print("⚽ REALIZANDO PREDICCIÓN DE CORNERS")
        print("=" * 60)
        print(f"📊 Modelo de corners: {type(model_corners).__name__}")
        print(f"🔧 Escalador: {type(scaler_corners).__name__}")
        print(f"🔢 Características enviadas: {features.shape[1]} features")
        print(f"📋 Features: {feature_columns}")
        print("-" * 60)
        
        # Escalar características
        print("🔧 Escalando características...")
        features_scaled = scaler_corners.transform(features)
        print(f"✅ Características escaladas: {features_scaled.shape}")
        
        # Agregar IDs de equipos (no escalados)
        equipo_local_array = np.array([[equipo_local_id]])
        equipo_visitante_array = np.array([[equipo_visitante_id]])
        
        # Combinar características escaladas con IDs
        features_final = np.hstack([features_scaled, equipo_local_array, equipo_visitante_array])
        print(f"✅ Características finales: {features_final.shape}")
        
        # Hacer predicción
        print("⚽ Prediciendo corners totales...")
        prediction = model_corners.predict(features_final)
        corners_totales = float(prediction[0])
        print(f"✅ Corners totales predichos: {corners_totales:.2f}")
        
        print("-" * 60)
        print(f"🎯 Predicción final: {corners_totales:.1f} corners totales")
        print("=" * 60)
        
        return {
            'corners_totales': corners_totales,
            'model_type': type(model_corners).__name__,
            'model_version': 'corners_v1',
            'scaler_type': type(scaler_corners).__name__,
            'prediction_note': '✅ Predicción de corners generada usando modelo de Machine Learning real',
            'features_used': feature_columns
        }
        
    except Exception as e:
        return {
            'error': f'Error en predicción de corners: {str(e)}',
            'corners_totales': None
        }

@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Endpoint para predicción de resultados
    Recibe: {equipo_local_id, equipo_visitante_id, fecha?}
    Devuelve: predicción de resultado del partido
    """
    try:
        print("\n" + "=" * 80)
        print("🌐 PETICIÓN RECIBIDA: /api/predict")
        print("=" * 80)
        
        data = request.get_json()
        
        if not data:
            print("❌ Error: No se recibieron datos")
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        equipo_local_id = data.get('equipo_local_id')
        equipo_visitante_id = data.get('equipo_visitante_id')
        fecha_request = data.get('fecha')  # Opcional
        
        print(f"🏠 Equipo Local ID: {equipo_local_id}")
        print(f"✈️ Equipo Visitante ID: {equipo_visitante_id}")
        print(f"📅 Fecha Request: {fecha_request}")
        
        if equipo_local_id is None or equipo_visitante_id is None:
            print("❌ Error: Faltan IDs de equipos")
            return jsonify({'error': 'Faltan IDs de equipos'}), 400
        
        # Determinar fecha de corte
        if fecha_request:
            # Si se proporciona fecha, usar la mínima entre la fecha del request y hoy
            fecha_hoy = datetime.now().strftime('%Y-%m-%d')
            fecha_corte = min(fecha_request, fecha_hoy)
        else:
            # Si no se proporciona fecha, usar hoy
            fecha_corte = datetime.now().strftime('%Y-%m-%d')
        
        # Hacer predicción de resultado
        result = predict_match_result(equipo_local_id, equipo_visitante_id, fecha_corte)
        
        if 'error' in result:
            return jsonify({
                'error': result['error'],
                'goles_local': None,
                'goles_visitante': None,
                'resultado_1x2': None
            }), 400
        
        # Preparar respuesta
        response = {
            'as_of': fecha_corte,
            'goles_local': result['goles_local'],
            'goles_visitante': result['goles_visitante'],
            'resultado_1x2': result['resultado_1x2'],
            'model_version': 'ligapro_v1',
            'model_type': type(model_resultados).__name__,
            'features_used': result.get('features_used', []),
            'cut_note': f'Predicción calculada solo con datos anteriores a {fecha_corte}',
            'prediction_note': '✅ Predicción generada usando modelo de Machine Learning real'
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

@app.route('/api/predict-corners', methods=['POST'])
def predict_corners_endpoint():
    """
    Endpoint para predicción de corners
    Recibe: {equipo_local_id, equipo_visitante_id}
    Devuelve: predicción de corners totales
    """
    try:
        print("\n" + "=" * 80)
        print("🌐 PETICIÓN RECIBIDA: /api/predict-corners")
        print("=" * 80)
        
        data = request.get_json()
        
        if not data:
            print("❌ Error: No se recibieron datos")
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        equipo_local_id = data.get('equipo_local_id')
        equipo_visitante_id = data.get('equipo_visitante_id')
        
        print(f"🏠 Equipo Local ID: {equipo_local_id}")
        print(f"✈️ Equipo Visitante ID: {equipo_visitante_id}")
        
        if equipo_local_id is None or equipo_visitante_id is None:
            print("❌ Error: Faltan IDs de equipos")
            return jsonify({'error': 'Faltan IDs de equipos'}), 400
        
        # Hacer predicción de corners
        result = predict_corners(equipo_local_id, equipo_visitante_id)
        
        if 'error' in result:
            return jsonify({
                'error': result['error'],
                'corners_totales': None
            }), 400
        
        # Preparar respuesta
        response = {
            'corners_totales': result['corners_totales'],
            'model_version': 'corners_v1',
            'model_type': type(model_corners).__name__,
            'scaler_type': type(scaler_corners).__name__,
            'features_used': result.get('features_used', []),
            'prediction_note': '✅ Predicción generada usando modelo de Machine Learning real'
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

@app.route('/api/historical-data', methods=['POST'])
def get_historical_data_endpoint():
    """
    Endpoint para obtener datos históricos de un enfrentamiento
    """
    try:
        print("\n" + "=" * 80)
        print("🌐 PETICIÓN RECIBIDA: /api/historical-data")
        print("=" * 80)
        
        data = request.get_json()
        
        if not data:
            print("❌ Error: No se recibieron datos")
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        equipo_local_id = data.get('equipo_local_id')
        equipo_visitante_id = data.get('equipo_visitante_id')
        
        print(f"🏠 Equipo Local ID: {equipo_local_id}")
        print(f"✈️ Equipo Visitante ID: {equipo_visitante_id}")
        
        if equipo_local_id is None or equipo_visitante_id is None:
            print("❌ Error: Faltan IDs de equipos")
            return jsonify({'error': 'Faltan IDs de equipos'}), 400
        
        # Obtener datos históricos de resultados
        result_data = get_average_result_data(equipo_local_id, equipo_visitante_id)
        
        # Obtener datos históricos de corners
        corners_data = get_average_match_data(equipo_local_id, equipo_visitante_id)
        
        # Obtener estadísticas del enfrentamiento
        enfrentamiento_data = get_enfrentamiento_stats(equipo_local_id, equipo_visitante_id)
        
        # Preparar respuesta con datos históricos
        response = {
            'resultados_historicos': {
                'ataques_local_promedio': float(result_data.get('ataques_local', 0)) if result_data else 0,
                'ataques_visitante_promedio': float(result_data.get('ataques_visitante', 0)) if result_data else 0,
                'posesion_local_promedio': float(result_data.get('posesion_local', 0)) if result_data else 50,
                'posesion_visitante_promedio': float(result_data.get('posesion_visitante', 0)) if result_data else 50,
                'corners_local_promedio': float(result_data.get('corners_local', 0)) if result_data else 0,
                'corners_visitante_promedio': float(result_data.get('corners_visitante', 0)) if result_data else 0,
                'num_partidos_resultados': int(result_data.get('num_partidos', 0)) if result_data else 0
            },
            'corners_historicos': {
                'corners_promedio_hist': float(corners_data.get('corners_vs_rival_hist', 0)) if corners_data else 0,
                'num_partidos_corners': int(corners_data.get('num_partidos', 0)) if corners_data else 0
            },
            'enfrentamiento_historico': {
                'total_partidos': int(enfrentamiento_data.get('total_partidos', 0)) if enfrentamiento_data else 0,
                'posesion_local_promedio': float(enfrentamiento_data.get('posesion_local_promedio', 0)) if enfrentamiento_data else 50,
                'posesion_visitante_promedio': float(enfrentamiento_data.get('posesion_visitante_promedio', 0)) if enfrentamiento_data else 50,
                'corners_promedio': float(enfrentamiento_data.get('corners_promedio', 0)) if enfrentamiento_data else 0,
                'goles_promedio': float(enfrentamiento_data.get('goles_promedio', 0)) if enfrentamiento_data else 0,
                'tarjetas_promedio': float(enfrentamiento_data.get('tarjetas_promedio', 0)) if enfrentamiento_data else 0,
                'victorias_local': int(enfrentamiento_data.get('victorias_local', 0)) if enfrentamiento_data else 0,
                'victorias_visitante': int(enfrentamiento_data.get('victorias_visitante', 0)) if enfrentamiento_data else 0,
                'empates': int(enfrentamiento_data.get('empates', 0)) if enfrentamiento_data else 0
            }
        }
        
        print(f"📊 Datos históricos obtenidos: {response['resultados_historicos']['num_partidos_resultados']} partidos resultados, {response['corners_historicos']['num_partidos_corners']} partidos corners")
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

def get_enfrentamiento_stats(equipo_local_id, equipo_visitante_id):
    """
    Obtener estadísticas del enfrentamiento histórico entre dos equipos
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            # Primero obtener todos los partidos entre los dos equipos
            sql = """
            SELECT * FROM resultado_historico_tabla 
            WHERE (equipo_local_id = %s AND equipo_visitante_id = %s) OR 
                  (equipo_local_id = %s AND equipo_visitante_id = %s)
            """
            cursor.execute(sql, (equipo_local_id, equipo_visitante_id, equipo_visitante_id, equipo_local_id))
            partidos = cursor.fetchall()
            
            if not partidos:
                print("❌ No se encontraron partidos históricos para este enfrentamiento")
                return None
            
            print(f"📊 Encontrados {len(partidos)} partidos totales entre ambos equipos")
            
            # Calcular estadísticas
            total_partidos = len(partidos)
            posesion_local_total = 0
            posesion_visitante_total = 0
            corners_total = 0
            goles_total = 0
            tarjetas_total = 0
            victorias_local = 0
            victorias_visitante = 0
            empates = 0
            
            for partido in partidos:
                # Posesión (convertir de decimal a porcentaje)
                posesion_local_total += float(partido['posesion_local']) * 100
                posesion_visitante_total += float(partido['posesion_visitante']) * 100
                
                # Corners totales (suma de local + visitante)
                corners_total += float(partido['corners_local']) + float(partido['corners_visitante'])
                
                # Goles totales (suma de local + visitante)
                goles_total += float(partido['goles_local']) + float(partido['goles_visitante'])
                
                # Tarjetas totales
                tarjetas_total += float(partido['tarjetas_totales'])
                
                # Victorias
                if partido['resultado_1x2'] == 1:
                    victorias_local += 1
                elif partido['resultado_1x2'] == 2:
                    victorias_visitante += 1
                else:
                    empates += 1
            
            # Calcular promedios
            result = {
                'total_partidos': total_partidos,
                'posesion_local_promedio': posesion_local_total / total_partidos,
                'posesion_visitante_promedio': posesion_visitante_total / total_partidos,
                'corners_promedio': corners_total / (total_partidos * 2),  # Dividir por 2 porque sumamos local + visitante
                'goles_promedio': goles_total / (total_partidos * 2),      # Dividir por 2 porque sumamos local + visitante
                'tarjetas_promedio': tarjetas_total / (total_partidos * 2), # Dividir por 2 porque tarjetas_totales ya es el total
                'victorias_local': victorias_local,
                'victorias_visitante': victorias_visitante,
                'empates': empates
            }
            
            return result
            
    except Exception as e:
        print(f"Error en consulta de enfrentamiento: {e}")
        return None
    finally:
        connection.close()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de salud del servidor"""
    return jsonify({
        'status': 'ok',
        'models_loaded': model_resultados is not None,
        'models_info': {
            'resultados_model': {
                'loaded': model_resultados is not None,
                'type': type(model_resultados).__name__ if model_resultados else None,
                'file': 'modelos/modelo_ligapro.pkl'
            },
            'corners_model': {
                'loaded': model_corners is not None,
                'type': type(model_corners).__name__ if model_corners else None,
                'file': 'modelos/prediccion_corners_totales.pkl'
            },
            'corners_scaler': {
                'loaded': scaler_corners is not None,
                'type': type(scaler_corners).__name__ if scaler_corners else None,
                'file': 'modelos/escalador_corners.pkl'
            }
        },
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/')
def index():
    """Servir la página principal"""
    return send_from_directory('public', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """Servir archivos estáticos"""
    return send_from_directory('public', filename)

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 INICIANDO SERVIDOR UPSBet")
    print("=" * 60)
    print(f"✅ Modelo de resultados: {'CARGADO' if model_resultados else 'NO CARGADO'}")
    print(f"✅ Modelo de corners: {'CARGADO' if model_corners else 'NO CARGADO'}")
    print(f"✅ Escalador de corners: {'CARGADO' if scaler_corners else 'NO CARGADO'}")
    print("=" * 60)
    print("🌐 Servidor disponible en: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
