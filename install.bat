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
echo 2. Creando entorno virtual...
if exist venv (
    echo Entorno virtual ya existe, eliminando...
    rmdir /s /q venv
)
python -m venv venv

echo.
echo 3. Activando entorno virtual...
call venv\Scripts\activate

echo.
echo 4. Actualizando pip...
python -m pip install --upgrade pip

echo.
echo 5. Instalando dependencias...
pip install -r requirements.txt

echo.
echo 6. Verificando instalacion...
python -c "import flask, psycopg2, sklearn, pandas, numpy, lightgbm, xgboost; print('Todas las dependencias instaladas correctamente')"

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
pause
