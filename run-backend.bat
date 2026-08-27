@echo off
setlocal
cd /d "%~dp0backend"

if not exist .venv (
  python -m venv .venv
)

call .venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto :error

python -m pip install -r requirements.txt
if errorlevel 1 goto :error

python -c "import igraph" >nul 2>&1
if errorlevel 1 goto :install_plot_dep
python -c "import cairo" >nul 2>&1
if not errorlevel 1 goto :run
python -c "import cairocffi" >nul 2>&1
if not errorlevel 1 goto :run

:install_plot_dep
echo Instalando dependencia de renderizacao do igraph...
python -m pip install pycairo
if not errorlevel 1 goto :run

echo pycairo nao foi instalado. Tentando cairocffi...
python -m pip install cairocffi
if errorlevel 1 goto :plot_error

:run
python -m uvicorn app.main:app --reload --port 8000
goto :eof

:plot_error
echo.
echo Falha ao instalar pycairo/cairocffi.
echo Delete a pasta backend\.venv e execute este arquivo novamente.
exit /b 1

:error
echo.
echo Falha ao instalar as dependencias do backend.
echo Se esta pasta foi copiada de outro local, apague backend\.venv e execute novamente.
exit /b 1
