#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento del backend UPSBet
"""

import requests
import json
import sys

def test_health_endpoint():
    """Probar endpoint de salud"""
    print("🔍 Probando endpoint de salud...")
    try:
        response = requests.get('http://localhost:5000/api/health')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Servidor funcionando - Modelos cargados: {data.get('models_loaded', False)}")
            return True
        else:
            print(f"❌ Error en health check: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor. ¿Está corriendo en localhost:5000?")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_prediction_endpoint():
    """Probar endpoint de predicción"""
    print("\n🔍 Probando endpoint de predicción...")
    
    # Datos de prueba
    test_data = {
        "home_name": "Emelec",
        "away_name": "Barcelona SC", 
        "home_code": 4,
        "away_code": 0
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/api/predict',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(test_data)
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Predicción exitosa!")
            print(f"   Corners totales: {data.get('corners_totales', 'N/A')}")
            print(f"   Home win: {data.get('home_win', 'N/A')}")
            print(f"   Draw: {data.get('draw', 'N/A')}")
            print(f"   Away win: {data.get('away_win', 'N/A')}")
            
            if 'error' in data:
                print(f"⚠️  Advertencia: {data['error']}")
            
            return True
        else:
            print(f"❌ Error en predicción: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_different_teams():
    """Probar con diferentes equipos"""
    print("\n🔍 Probando con diferentes equipos...")
    
    test_cases = [
        {"home": "LDU de Quito", "away": "Independiente del Valle", "home_code": 5, "away_code": 7},
        {"home": "Deportivo Cuenca", "away": "Aucas", "home_code": 10, "away_code": 12},
        {"home": "Mushuc Runa SC", "away": "Universidad Catolica", "home_code": 6, "away_code": 13}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"   Prueba {i}: {test_case['home']} vs {test_case['away']}")
        
        test_data = {
            "home_name": test_case["home"],
            "away_name": test_case["away"],
            "home_code": test_case["home_code"],
            "away_code": test_case["away_code"]
        }
        
        try:
            response = requests.post(
                'http://localhost:5000/api/predict',
                headers={'Content-Type': 'application/json'},
                data=json.dumps(test_data)
            )
            
            if response.status_code == 200:
                data = response.json()
                corners = data.get('corners_totales', 'N/A')
                print(f"      ✅ Corners: {corners}")
            else:
                print(f"      ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas del backend UPSBet...")
    print("=" * 50)
    
    # Probar health endpoint
    if not test_health_endpoint():
        print("\n❌ El servidor no está funcionando correctamente.")
        print("   Asegúrate de ejecutar: python app.py")
        sys.exit(1)
    
    # Probar predicción
    if not test_prediction_endpoint():
        print("\n❌ Error en el endpoint de predicción.")
        sys.exit(1)
    
    # Probar diferentes equipos
    test_different_teams()
    
    print("\n" + "=" * 50)
    print("✅ Todas las pruebas completadas!")
    print("\n💡 Para usar el frontend:")
    print("   1. Abre public/index.html en tu navegador")
    print("   2. Selecciona equipos y haz clic en 'Predecir'")
    print("   3. Verás la predicción de corners totales")

if __name__ == "__main__":
    main()
