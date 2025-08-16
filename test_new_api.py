#!/usr/bin/env python3
"""
Script para probar la nueva API de predicción de resultados
"""

import requests
import json

def test_api():
    print("=" * 60)
    print("PRUEBA DE API DE PREDICCIÓN DE RESULTADOS")
    print("=" * 60)
    
    # Probar endpoint de salud
    print("\n1. Probando API de salud...")
    try:
        response = requests.get("http://localhost:5000/api/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Modelos cargados: {data.get('models_loaded')}")
            print(f"✅ Status: {data.get('status')}")
        else:
            print("❌ Error en health check")
            return
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return
    
    # Probar predicción
    print("\n2. Probando predicción de resultado...")
    payload = {
        "equipo_local_id": 4,  # Emelec
        "equipo_visitante_id": 0  # Barcelona SC
    }
    
    print(f"Datos enviados: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            "http://localhost:5000/api/predict",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Predicción exitosa:")
            print(json.dumps(data, indent=2))
            
            # Mostrar resultado de forma legible
            if data.get('goles_local') and data.get('goles_visitante'):
                local_goals = data['goles_local']['rounded']
                away_goals = data['goles_visitante']['rounded']
                resultado = data.get('resultado_1x2')
                
                resultado_texto = {
                    1: "Victoria Local",
                    0: "Empate", 
                    2: "Victoria Visitante"
                }.get(resultado, "Desconocido")
                
                print(f"\n🎯 RESULTADO:")
                print(f"   Marcador: {local_goals} - {away_goals}")
                print(f"   Resultado: {resultado_texto}")
                print(f"   Fecha de corte: {data.get('as_of')}")
                print(f"   Modelo: {data.get('model_version')}")
                
        else:
            print("❌ Error en predicción:")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error en predicción: {e}")
    
    print("\n" + "=" * 60)
    print("PRUEBA COMPLETADA")
    print("=" * 60)

if __name__ == "__main__":
    test_api()


