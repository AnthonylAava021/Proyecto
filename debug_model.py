import pickle
import os

print("Verificando modelo...")

# Verificar archivo
if os.path.exists('modelos/modelo_ligapro.pkl'):
    print(f"✅ Archivo existe: {os.path.getsize('modelos/modelo_ligapro.pkl')} bytes")
else:
    print("❌ Archivo no existe")
    exit()

# Intentar diferentes métodos de carga
encodings = [None, 'latin1', 'utf-8', 'cp1252']

for encoding in encodings:
    try:
        print(f"\nIntentando con encoding: {encoding}")
        with open('modelos/modelo_ligapro.pkl', 'rb') as f:
            if encoding:
                model = pickle.load(f, encoding=encoding)
            else:
                model = pickle.load(f)
        print(f"✅ Éxito con encoding: {encoding}")
        print(f"   Tipo: {type(model)}")
        break
    except Exception as e:
        print(f"❌ Error con encoding {encoding}: {e}")
        continue
else:
    print("\n❌ No se pudo cargar el modelo con ningún encoding")


