import pickle

try:
    with open('modelos/modelo_ligapro.pkl', 'rb') as f:
        model = pickle.load(f)
    print(f"Modelo cargado: {type(model)}")
    print("✅ Éxito")
except Exception as e:
    print(f"❌ Error: {e}")


