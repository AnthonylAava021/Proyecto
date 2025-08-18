# 🏆 UPSBet - Sistema de Predicción de Fútbol

Sistema completo de predicción de partidos de fútbol usando Machine Learning para la Liga Profesional de Fútbol Ecuatoriano.

## 🚀 Características

- **Predicción de Resultados**: Goles local y visitante
- **Predicción de Corners**: Corners totales del partido
- **Predicción de Tarjetas**: Tarjetas totales del partido
- **Datos Históricos**: Estadísticas de enfrentamientos
- **Interfaz Web Moderna**: Diseño responsive y atractivo
- **Modelos de ML Reales**: LightGBM, XGBoost y modelos personalizados

## 📋 Requisitos Previos

### Software Necesario
- **Python 3.8+** (recomendado 3.11)
- **PostgreSQL 12+**
- **Git** (para clonar el repositorio)

### Base de Datos
- PostgreSQL configurado con:
  - Base de datos: `UPS_BET`
  - Usuario: `user`
  - Contraseña: `ups_bet05`
  - Puerto: `5432`

## 🛠️ Instalación

### 1. Clonar el Repositorio
```bash
git clone <url-del-repositorio>
cd Proyecto
```

### 2. Crear Entorno Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos

#### Opción A: Usar archivos SQL proporcionados
```bash
# Conectar a PostgreSQL
psql -U user -d UPS_BET

# Ejecutar los archivos SQL en orden:
\i data/datos_tabla_corners.sql
\i data/datos_tabla_ganador_resultado.sql
\i data/datos_tabla_historico_resultado.sql
\i data/datos_tabla_tarjetas.sql
```

#### Opción B: Crear base de datos desde cero
```sql
-- Crear base de datos
CREATE DATABASE UPS_BET;

-- Crear usuario
CREATE USER user WITH PASSWORD 'ups_bet05';
GRANT ALL PRIVILEGES ON DATABASE UPS_BET TO user;
```

### 5. Verificar Modelos
Asegúrate de que los siguientes archivos estén en la carpeta `modelos/`:
- `modelo_ligapro.pkl` - Modelo de predicción de resultados
- `prediccion_corners_totales.pkl` - Modelo de predicción de corners
- `modelo_lightgbm_final.pkl` - Modelo de predicción de tarjetas
- `escalador_corners.pkl` - Escalador para datos de corners

## 🚀 Ejecución

### 1. Iniciar el Servidor
```bash
python app.py
```

### 2. Acceder a la Aplicación
Abre tu navegador y ve a: `http://localhost:5000`

## 📊 Funcionalidades

### Predicción de Resultados
- Predice goles local y visitante
- Determina resultado 1X2
- Usa modelos LightGBM entrenados

### Predicción de Corners
- Predice corners totales del partido
- Usa modelo XGBoost con escalado de datos
- Considera estadísticas históricas

### Predicción de Tarjetas
- Predice tarjetas totales del partido
- Usa modelo LightGBM especializado
- Analiza patrones de tarjetas históricas

### Datos Históricos
- Estadísticas de enfrentamientos directos
- Promedios de posesión, goles, corners
- Balance de victorias/empates/derrotas

## 🏗️ Estructura del Proyecto

```
Proyecto/
├── app.py                 # Servidor Flask principal
├── requirements.txt       # Dependencias Python
├── README.md             # Este archivo
├── data/                 # Archivos SQL de base de datos
│   ├── datos_tabla_corners.sql
│   ├── datos_tabla_ganador_resultado.sql
│   ├── datos_tabla_historico_resultado.sql
│   └── datos_tabla_tarjetas.sql
├── modelos/              # Modelos de Machine Learning
│   ├── modelo_ligapro.pkl
│   ├── prediccion_corners_totales.pkl
│   ├── modelo_lightgbm_final.pkl
│   └── escalador_corners.pkl
└── public/               # Archivos del frontend
    ├── index.html        # Página principal
    ├── css/              # Estilos
    ├── js/               # JavaScript
    ├── img/              # Imágenes y logos
    └── audio/            # Archivos de audio
```

## 🔧 Configuración

### Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto:
```env
DB_HOST=localhost
DB_USER=user
DB_PASSWORD=ups_bet05
DB_NAME=UPS_BET
DB_PORT=5432
```

### Configuración de Base de Datos
Los parámetros de conexión están en `app.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'user',
    'password': 'ups_bet05',
    'database': 'UPS_BET',
    'port': 5432
}
```

## 🧪 Pruebas

### Verificar Instalación
```bash
# Probar endpoint de salud
curl http://localhost:5000/api/health

# Probar predicción
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"equipo_local_id": 4, "equipo_visitante_id": 0}'
```

### Equipos Disponibles
- Barcelona SC (ID: 0)
- El Nacional (ID: 2)
- Emelec (ID: 4)
- LDU de Quito (ID: 5)
- Mushuc Runa SC (ID: 6)
- Independiente del Valle (ID: 7)
- CD Tecnico Universitario (ID: 8)
- Delfin (ID: 9)
- Deportivo Cuenca (ID: 10)
- Aucas (ID: 12)
- Universidad Catolica (ID: 13)
- CSD Macara (ID: 14)
- Orense SC (ID: 15)
- Manta FC (ID: 17)
- Libertad (ID: 20)
- Vinotinto (ID: 22)

## 🔍 Endpoints API

### Predicción de Resultados
```
POST /api/predict
{
  "equipo_local_id": 4,
  "equipo_visitante_id": 0
}
```

### Predicción de Corners
```
POST /api/predict-corners
{
  "equipo_local_id": 4,
  "equipo_visitante_id": 0
}
```

### Predicción de Tarjetas
```
POST /api/predict-tarjetas
{
  "equipo_local_id": 4,
  "equipo_visitante_id": 0
}
```

### Datos Históricos
```
POST /api/historical-data
{
  "equipo_local_id": 4,
  "equipo_visitante_id": 0
}
```

### Estado del Servidor
```
GET /api/health
```

## 🐛 Solución de Problemas

### Error de Conexión a Base de Datos
- Verificar que PostgreSQL esté corriendo
- Confirmar credenciales en `app.py`
- Verificar que la base de datos `UPS_BET` exista

### Error de Modelos
- Verificar que todos los archivos `.pkl` estén en `modelos/`
- Confirmar que las versiones de scikit-learn sean compatibles

### Error de Puerto
- Cambiar puerto en `app.py` si el 5000 está ocupado
- Verificar que no haya otros servicios usando el puerto

## 📝 Notas Importantes

- **Margen de Error**: Las predicciones tienen un margen de error de ±0.90
- **Datos Históricos**: Las predicciones se basan en datos hasta la fecha actual
- **Responsabilidad**: Juega con responsabilidad, no nos responsabilizamos por pérdidas

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o preguntas:
- Crear un issue en el repositorio
- Contactar al equipo de desarrollo

---

**¡Disfruta usando UPSBet! ⚽🏆**
