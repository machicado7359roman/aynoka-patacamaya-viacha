@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    set "PY=py"
) else (
    set "PY=python"
)

echo ================================================
echo NASA POWER - IVAN - PATACAMAYA Y VIACHA
echo ================================================

%PY% --version
if errorlevel 1 (
    echo No se encontro Python. Instala Python 3 y marca Add Python to PATH.
    pause
    exit /b 1
)

echo.
echo Instalando/verificando bibliotecas...
%PY% -m pip install -r requirements.txt
if errorlevel 1 (
    echo Error al instalar las bibliotecas.
    pause
    exit /b 1
)

echo.
echo Ejecutando descarga NASA POWER...
%PY% descargar_datos.py
if errorlevel 1 (
    echo La descarga termino con errores. Lee el mensaje anterior.
    pause
    exit /b 1
)

echo.
echo Proceso terminado. Revisa la carpeta resultados\procesados.
pause
