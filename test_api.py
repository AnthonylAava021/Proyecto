#!/usr/bin/env python3
"""
Script para probar la API de predicción
"""

import requests
import json

def test_predict_api():
    """Probar el endpoint de predicción"""
    url = "http://localhost:5000/api/predict"
    
    # Datos de prueba
    data = {
        "home_code": 4,
        "away_code": 0,
        "home_name": "Emelec",
        "away_name": "Barcelona SC"
    }
    
    print("Probando API de predicción...")
    print(f"URL: {url}")
    print(f"Datos: {json.dumps(data, indent=2)}")
    print()
    
    try:
        response = requests.post(url, json=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Respuesta exitosa:")
            print(json.dumps(result, indent=2))
        else:
            print("❌ Error en la respuesta:")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_health_api():
    """Probar el endpoint de salud"""
    url = "http://localhost:5000/api/health"
    
    print("Probando API de salud...")
    print(f"URL: {url}")
    print()
    
    try:
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Respuesta exitosa:")
            print(json.dumps(result, indent=2))
        else:
            print("❌ Error en la respuesta:")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def main():
    """Función principal"""
    print("=" * 50)
    print("PRUEBA DE API")
    print("=" * 50)
    print()
    
    # Probar health endpoint
    test_health_api()
    print()
    
    # Probar predict endpoint
    test_predict_api()
    
    print("=" * 50)
    print("PRUEBA COMPLETADA")
    print("=" * 50)

if __name__ == "__main__":
    main()
