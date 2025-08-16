# UPSBet - Predicción de Corners en Fútbol

Sistema de predicción de corners totales en partidos de fútbol usando Machine Learning.

## Estructura del Proyecto

```
Proyecto/
├── app.py                 # Backend Flask
├── requirements.txt       # Dependencias Python
├── README.md             # Este archivo
├── modelos/              # Modelos de ML
│   ├── escalador_corners.pkl
│   └── prediccion_corners_totales.pkl
├── data/                 # Datos SQL
│   ├── datos_tabla_corners.sql
│   └── datos_tabla_ganador_resultado.sql
└── public/               # Frontend
    ├── index.html
    ├── css/
    ├── js/
    └── img/
```

## Requisitos Previos

1. **Python 3.8+**
2. **PostgreSQL** con la base de datos `UPS_BET`
3. **Node.js** (opcional, para desarrollo)

## Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd Proyecto
```

### 2. Instalar dependencias Python
```bash
pip install -r requirements.txt
```

### 3. Configurar la base de datos
- Asegúrate de que PostgreSQL esté corriendo
- Crea la base de datos `UPS_BET`
- Importa los datos desde `data/datos_tabla_corners.sql`
- Verifica que el usuario `user` con contraseña `ups_bet05` tenga acceso

### 4. Verificar modelos
- Los modelos deben estar en la carpeta `modelos/`
- `escalador_corners.pkl`
- `prediccion_corners_totales.pkl`

### 5. Verificar configuración
```bash
python check_db_structure.py
```

### 6. Verificar y solucionar problemas con modelos
```bash
python fix_models.py
```

## Uso

### Iniciar el Servidor Completo
```bash
python run_server.py
```

O alternativamente:
```bash
python app.py
```

El servidor se iniciará en `http://localhost:5000`

### Acceder a la Aplicación
- **Frontend**: http://localhost:5000
- **API Backend**: http://localhost:5000/api/
- **Health Check**: http://localhost:5000/api/health

### Endpoints Disponibles

- `POST /api/predict` - Predicción de corners
- `GET /api/health` - Estado del servidor

## Flujo de Predicción

1. **Frontend**: Usuario selecciona equipos local y visitante
2. **Backend**: Recibe códigos de equipos (IDs)
3. **Base de Datos**: Busca último enfrentamiento en `corners_tabla`
4. **Modelo**: Escala datos y hace predicción
5. **Respuesta**: Devuelve corners totales al frontend

## Configuración de Base de Datos

```sql
-- Crear base de datos
CREATE DATABASE UPS_BET;

-- Crear usuario
CREATE USER user WITH PASSWORD 'ups_bet05';
GRANT ALL PRIVILEGES ON DATABASE UPS_BET TO user;

-- Conectar a la base de datos
\c UPS_BET

-- Importar datos
\i data/datos_tabla_corners.sql
```

## Equipos Disponibles

Los equipos están codificados con los siguientes IDs:
- Barcelona SC: 0
- El Nacional: 2
- Emelec: 4
- LDU de Quito: 5
- Mushuc Runa SC: 6
- Independiente del Valle: 7
- CD Tecnico Universitario: 8
- Delfin: 9
- Deportivo Cuenca: 10
- Aucas: 12
- Universidad Catolica: 13
- CSD Macara: 14
- Orense SC: 15
- Manta FC: 17
- Libertad: 20
- Vinotinto: 22

## Solución de Problemas

### Error de conexión a base de datos
- Verifica que PostgreSQL esté corriendo
- Confirma credenciales en `app.py`
- Asegúrate de que la base de datos `UPS_BET` existe

### Error cargando modelos
- Verifica que los archivos `.pkl` estén en la carpeta `modelos/`
- Confirma que tienes scikit-learn instalado

### Error de predicción
- Revisa los logs del servidor
- Verifica que la tabla `corners_tabla` tenga datos
- Confirma que las columnas coincidan con lo esperado por el modelo

## Desarrollo

### Modificar configuración de BD
Edita las variables en `app.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'user',
    'password': 'ups_bet05',
    'database': 'UPS_BET',
    'port': 5432
}
```

### Agregar nuevos equipos
1. Actualiza `equipos_dict` en `public/js/script.js`
2. Agrega logo en `public/img/`
3. Actualiza `NAME_TO_FILE` en `public/js/script.js`

## Licencia

Este proyecto es para uso educativo y de investigación.
