@echo off
echo ========================================
echo UPSBet - Instalacion Automatica
echo ========================================
echo.

echo 1. Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor instala Python 3.8+ desde https://python.org
    pause
    exit /b 1
)

echo.
echo 2. Verificando PostgreSQL...
echo Intentando conectar a PostgreSQL...
python -c "import psycopg2; conn=psycopg2.connect(host='localhost', user='user', password='ups_bet05', database='UPS_BET', port=5432); print('PostgreSQL conectado exitosamente'); conn.close()" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ADVERTENCIA: No se pudo conectar a PostgreSQL
    echo.
    echo Para configurar PostgreSQL:
    echo 1. Instalar PostgreSQL desde https://postgresql.org
    echo 2. Crear base de datos: CREATE DATABASE "UPS_BET";
    echo 3. Crear usuario: CREATE USER "user" WITH PASSWORD 'ups_bet05';
    echo 4. Dar permisos: GRANT ALL PRIVILEGES ON DATABASE "UPS_BET" TO "user";
    echo.
    echo ¿Deseas continuar con la instalación? (s/n)
    set /p continue=
    if /i not "%continue%"=="s" exit /b 1
)

echo.
echo 3. Verificando archivos de modelos...
if not exist "modelos\modelo_ligapro.pkl" (
    echo ERROR: Falta archivo modelos\modelo_ligapro.pkl
    echo Asegúrate de que todos los archivos de modelos estén en la carpeta modelos\
    pause
    exit /b 1
)
if not exist "modelos\prediccion_corners_totales.pkl" (
    echo ERROR: Falta archivo modelos\prediccion_corners_totales.pkl
    pause
    exit /b 1
)
if not exist "modelos\modelo_lightgbm_final.pkl" (
    echo ERROR: Falta archivo modelos\modelo_lightgbm_final.pkl
    pause
    exit /b 1
)
if not exist "modelos\escalador_corners.pkl" (
    echo ERROR: Falta archivo modelos\escalador_corners.pkl
    pause
    exit /b 1
)
echo ✅ Todos los archivos de modelos encontrados

echo.
echo 4. Creando entorno virtual...
if exist venv (
    echo Entorno virtual ya existe, eliminando...
    rmdir /s /q venv
)
python -m venv venv

echo.
echo 5. Activando entorno virtual...
call venv\Scripts\activate

echo.
echo 6. Actualizando pip...
python -m pip install --upgrade pip

echo.
echo 7. Instalando dependencias...
pip install -r requirements.txt

echo.
echo 8. Verificando instalacion...
python -c "import flask, psycopg2, sklearn, pandas, numpy, lightgbm, xgboost; print('✅ Todas las dependencias instaladas correctamente')"

echo.
echo 9. Verificando modelos...
python check_model.py

echo.
echo ========================================
echo Instalacion completada exitosamente!
echo ========================================
echo.
echo Para iniciar el servidor:
echo 1. Activa el entorno virtual: venv\Scripts\activate
echo 2. Ejecuta: python app.py
echo 3. Abre: http://localhost:5000
echo.
echo IMPORTANTE: Asegurate de tener PostgreSQL configurado
echo con la base de datos UPS_BET antes de ejecutar.
echo.
echo Para verificar el estado del servidor:
echo http://localhost:5000/api/health
echo.
pause
