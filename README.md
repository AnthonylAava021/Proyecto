# UPSBet - Sistema de Predicción de Fútbol

## 📋 Requisitos Previos

### 1. Python
- **Versión:** Python 3.8 o superior
- **Descarga:** https://python.org

### 2. PostgreSQL (OBLIGATORIO)
- **Versión:** PostgreSQL 12 o superior
- **Descarga:** https://postgresql.org

#### Configuración de PostgreSQL:
1. Instalar PostgreSQL
2. Crear una base de datos llamada `UPS_BET`
3. Crear un usuario con los siguientes datos:
   - **Usuario:** `credencialesdelgrupo`
   - **Contraseña:** `credencialesdelgrupo`
   - **Permisos:** Acceso completo a la base de datos `UPS_BET`

#### Comandos SQL para configurar:
```sql
CREATE DATABASE "credencialesdelgrupo";
CREATE USER "credencialesdelgrupo" WITH PASSWORD 'credencialesdelgrupo';
GRANT ALL PRIVILEGES ON DATABASE "credencialesdelgrupo" TO "credencialesdelgrupo";
```

### 3. Archivos de Modelos
Asegúrate de que los siguientes archivos estén en la carpeta `modelos/`:
- `modelo_ligapro.pkl`
- `prediccion_corners_totales.pkl`
- `modelo_lightgbm_final.pkl`
- `escalador_corners.pkl`

## 🚀 Instalación Automática (Windows)

### Opción 1: Script Automático
```bash
# Ejecutar el archivo install.bat
install.bat
```

### Opción 2: Instalación Manual

1. **Clonar el repositorio:**
```bash
git clone [URL_DEL_REPOSITORIO]
cd Proyecto
```

2. **Crear entorno virtual:**
```bash
python -m venv venv
```

3. **Activar entorno virtual:**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

## 🗄️ Configuración de la Base de Datos

### Importar Datos (si es necesario):
Los archivos SQL están en la carpeta `data/`:
- `datos_tabla_corners.sql`
- `datos_tabla_ganador_resultado.sql`
- `datos_tabla_historico_resultado.sql`
- `datos_tabla_tarjetas.sql`

Para importar:
```bash
psql -U user -d UPS_BET -f data/datos_tabla_corners.sql
psql -U user -d UPS_BET -f data/datos_tabla_ganador_resultado.sql
psql -U user -d UPS_BET -f data/datos_tabla_historico_resultado.sql
psql -U user -d UPS_BET -f data/datos_tabla_tarjetas.sql
```

## 🏃‍♂️ Ejecutar el Servidor

1. **Activar entorno virtual:**
```bash
venv\Scripts\activate
```

2. **Ejecutar la aplicación:**
```bash
python app.py
```

3. **Abrir en el navegador:**
```
http://localhost:5000
```

## 🔧 Solución de Problemas

### Error: "No module named 'psycopg2'"
```bash
pip install psycopg2-binary
```

### Error: "Connection refused" (PostgreSQL)
- Verificar que PostgreSQL esté ejecutándose
- Verificar configuración en `app.py` líneas 18-24

### Error: "Model not found"
- Verificar que los archivos `.pkl` estén en la carpeta `modelos/`
- Verificar permisos de lectura

### Error: "Port already in use"
```bash
# Cambiar puerto en app.py línea 1177
app.run(debug=True, host='0.0.0.0', port=5001)
```

## 📊 Verificar Instalación

Ejecutar el endpoint de salud:
```
http://localhost:5000/api/health
```

Debería devolver:
```json
{
  "status": "ok",
  "models_loaded": true,
  "models_info": {...}
}
```

## 📁 Estructura del Proyecto

```
Proyecto/
├── app.py                 # Servidor principal
├── requirements.txt       # Dependencias
├── install.bat           # Script de instalación
├── modelos/              # Modelos de ML
├── data/                 # Datos SQL
├── public/               # Archivos web
└── README.md            # Este archivo
```

## 🆘 Soporte

Si tienes problemas:
1. Verificar que PostgreSQL esté instalado y configurado
2. Verificar que todos los archivos de modelos estén presentes
3. Revisar los logs del servidor para errores específicos
4. Ejecutar `python check_model.py` para verificar modelos
