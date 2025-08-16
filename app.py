from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import pickle
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
        # Cargar escalador
        with open('modelos/escalador_corners.pkl', 'rb') as f:
            scaler = pickle.load(f)
        
        # Cargar modelo
        with open('modelos/prediccion_corners_totales.pkl', 'rb') as f:
            model = pickle.load(f)
        
        return scaler, model
    except Exception as e:
        print(f"Error cargando modelos: {e}")
        return None, None

scaler, model = load_models()

def get_db_connection():
    """Crear conexión a la base de datos PostgreSQL"""
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        print(f"Tipo de error: {type(e)}")
        return None

def get_last_match_data(equipo_local_id, equipo_visita_id):
    """
    Obtener el último registro del enfrentamiento entre dos equipos
    Si no existe, intentar con los equipos intercambiados
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            # Primera consulta: equipo_local_id vs equipo_visitante_id
            sql = """
            SELECT * FROM corners_tabla 
            WHERE equipo_local_id = %s AND equipo_visitante_id = %s 
            ORDER BY fecha DESC 
            LIMIT 1
            """
            cursor.execute(sql, (equipo_local_id, equipo_visita_id))
            result = cursor.fetchone()
            
            if result:
                return dict(result)
            
            # Segunda consulta: equipo_visitante_id vs equipo_local_id (intercambiados)
            sql = """
            SELECT * FROM corners_tabla 
            WHERE equipo_local_id = %s AND equipo_visitante_id = %s 
            ORDER BY fecha DESC 
            LIMIT 1
            """
            cursor.execute(sql, (equipo_visita_id, equipo_local_id))
            result = cursor.fetchone()
            
            if result:
                return dict(result)
            
            return None
            
    except Exception as e:
        print(f"Error en consulta de base de datos: {e}")
        return None
    finally:
        connection.close()

def prepare_features(match_data):
    """
    Preparar las características para el modelo
    Incluir equipo_local_id y equipo_visitante_id sin escalar
    """
    if not match_data:
        return None
    
    # Convertir a DataFrame
    df = pd.DataFrame([match_data])
    
    # Columnas que NO son características (excluir)
    exclude_columns = ['fecha', 'id']
    
    # Obtener solo las columnas de características (incluyendo los IDs)
    feature_columns = [col for col in df.columns if col not in exclude_columns]
    
    # Si no hay columnas de características, usar todas excepto las excluidas
    if not feature_columns:
        feature_columns = [col for col in df.columns if col not in exclude_columns]
    
    features = df[feature_columns].values
    
    return features, feature_columns

def predict_corners(equipo_local_id, equipo_visita_id):
    """
    Predecir corners totales para un enfrentamiento
    """
    # Verificar que los modelos estén cargados
    if scaler is None or model is None:
        return {
            'error': 'Los modelos de predicción no están disponibles',
            'corners_totales': None
        }
    
    # Obtener datos del último enfrentamiento
    match_data = get_last_match_data(equipo_local_id, equipo_visita_id)
    
    if not match_data:
        return {
            'error': 'No se encontraron datos históricos para este enfrentamiento',
            'corners_totales': None
        }
    
    # Preparar características
    features, feature_columns = prepare_features(match_data)
    
    if features is None:
        return {
            'error': 'Error preparando características para el modelo',
            'corners_totales': None
        }
    
    try:
        # Separar características que se escalan vs las que no
        # Los IDs (equipo_local_id, equipo_visitante_id) no se escalan
        id_columns = ['equipo_local_id', 'equipo_visitante_id']
        numeric_columns = [col for col in feature_columns if col not in id_columns]
        
        # Obtener índices de las columnas
        id_indices = [feature_columns.index(col) for col in id_columns if col in feature_columns]
        numeric_indices = [feature_columns.index(col) for col in numeric_columns if col in feature_columns]
        
        # Crear array final con 18 características
        final_features = np.zeros((1, 18))
        
        # Colocar características escaladas en las primeras 16 posiciones
        if numeric_indices:
            numeric_features = features[:, numeric_indices]
            features_scaled = scaler.transform(numeric_features)
            final_features[0, :16] = features_scaled[0]
        
        # Colocar IDs sin escalar en las posiciones 16 y 17
        if len(id_indices) >= 2:
            final_features[0, 16] = features[0, id_indices[0]]  # equipo_local_id
            final_features[0, 17] = features[0, id_indices[1]]  # equipo_visitante_id
        
        # Hacer predicción
        prediction = model.predict(final_features)
        
        # El modelo devuelve un array, tomar el primer valor
        corners_totales = float(prediction[0])
        
        return {
            'corners_totales': corners_totales,
            'features_used': feature_columns,
            'match_data': match_data
        }
        
    except Exception as e:
        return {
            'error': f'Error en predicción: {str(e)}',
            'corners_totales': None
        }

@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Endpoint para predicción
    Recibe: {home_code, away_code, home_name, away_name}
    Devuelve: predicción de corners totales
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        home_code = data.get('home_code')
        away_code = data.get('away_code')
        home_name = data.get('home_name')
        away_name = data.get('away_name')
        
        if home_code is None or away_code is None:
            return jsonify({'error': 'Faltan códigos de equipos'}), 400
        
        # Hacer predicción de corners
        corners_result = predict_corners(home_code, away_code)
        
        if 'error' in corners_result:
            return jsonify({
                'error': corners_result['error'],
                'corners_totales': None
            }), 400
        
        # Devolver solo la predicción de corners
        response = {
            'corners_totales': corners_result['corners_totales']
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de salud del servidor"""
    return jsonify({
        'status': 'ok',
        'models_loaded': scaler is not None and model is not None,
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
    print("Iniciando servidor UPSBet...")
    print(f"Modelos cargados: {scaler is not None and model is not None}")
    app.run(debug=True, host='0.0.0.0', port=5000)
