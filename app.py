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
    Preparar características para el modelo de predicción de resultados
    """
    # Obtener datos históricos hasta la fecha de corte
    historical_data = get_historical_data(fecha_corte)
    if historical_data is None:
        return None, None
    
    # Convertir a DataFrame
    df_corte = pd.DataFrame(historical_data)
    
    if df_corte.empty:
        return None, None
    
    # Calcular estadísticas de ambos equipos
    local_stats = get_team_stats(df_corte, equipo_local_id, is_local=True)
    away_stats = get_team_stats(df_corte, equipo_visitante_id, is_local=False)
    
    # Obtener las características esperadas del modelo
    expected_features = model_resultados['feature_columns'].tolist()
    
    # Crear características para el modelo con valores por defecto
    features = {}
    for feature in expected_features:
        if feature == 'equipo_local_id':
            features[feature] = equipo_local_id
        elif feature == 'equipo_visitante_id':
            features[feature] = equipo_visitante_id
        else:
            # Para otras características, usar valores por defecto basados en estadísticas
            if 'local' in feature:
                if 'goles' in feature:
                    features[feature] = local_stats.get('goles_promedio', 1.0)
                elif 'posesion' in feature:
                    features[feature] = 50.0  # Valor por defecto
                else:
                    features[feature] = 5.0  # Valor por defecto para otras métricas
            elif 'visitante' in feature:
                if 'goles' in feature:
                    features[feature] = away_stats.get('goles_promedio', 1.0)
                elif 'posesion' in feature:
                    features[feature] = 50.0  # Valor por defecto
                else:
                    features[feature] = 5.0  # Valor por defecto para otras métricas
            else:
                # Para características totales
                features[feature] = 10.0  # Valor por defecto
    
    features_array = np.array([[features[col] for col in expected_features]])
    
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
            'error': 'Error preparando características para el modelo',
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

def get_last_match_data(equipo_local_id, equipo_visitante_id):
    """
    Obtener el último registro de un enfrentamiento específico
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            # Buscar enfrentamiento directo
            sql = """
            SELECT * FROM corners_tabla 
            WHERE equipo_local_id = %s AND equipo_visitante_id = %s 
            ORDER BY fecha DESC 
            LIMIT 1
            """
            cursor.execute(sql, (equipo_local_id, equipo_visitante_id))
            result = cursor.fetchone()
            
            if result:
                return dict(result)
            
            # Si no existe, buscar enfrentamiento inverso
            sql = """
            SELECT * FROM corners_tabla 
            WHERE equipo_local_id = %s AND equipo_visitante_id = %s 
            ORDER BY fecha DESC 
            LIMIT 1
            """
            cursor.execute(sql, (equipo_visitante_id, equipo_local_id))
            result = cursor.fetchone()
            
            if result:
                return dict(result)
            
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
    
    # Columnas a excluir (no son características numéricas)
    exclude_columns = ['id', 'fecha', 'equipo_local_id', 'equipo_visitante_id']
    
    # Extraer características numéricas
    features = {}
    for key, value in match_data.items():
        if key not in exclude_columns and isinstance(value, (int, float)):
            features[key] = value
    
    # Ordenar características para mantener consistencia
    feature_columns = sorted(features.keys())
    features_array = np.array([[features[col] for col in feature_columns]])
    
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
    
    # Obtener datos del último partido
    match_data = get_last_match_data(equipo_local_id, equipo_visitante_id)
    
    if not match_data:
        return {
            'error': 'No se encontraron datos históricos para este enfrentamiento',
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
