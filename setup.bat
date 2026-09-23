@echo off
setlocal
cd /d "%~dp0"
title Sbobiner - installazione

echo.
echo  Sbobiner - installazione (una volta sola, serve internet)
echo.

rem --- Python 3.10 o superiore ---
set "PY="
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul && set "PY=py -3"
if not defined PY python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul && set "PY=python"
if defined PY goto :venv

echo Python 3.10 o superiore non trovato.
where winget >nul 2>nul || goto :nopython
choice /c SN /m "Vuoi installarlo adesso (Python 3.12, tramite winget)"
if errorlevel 2 goto :nopython
rem x64 anche sui PC ARM: le librerie di trascrizione esistono solo per x64
winget install -e --id Python.Python.3.12 --architecture x64 --accept-package-agreements --accept-source-agreements
echo.
echo Python installato. Chiudi questa finestra e rifai doppio click su setup.bat.
pause
exit /b 0

:nopython
echo Installa Python 3.12 da https://www.python.org/downloads/windows/
echo (spunta "Add python.exe to PATH"), poi rifai doppio click su setup.bat.
pause
exit /b 1

:venv
echo ==^> Creo l'ambiente virtuale (.venv)
%PY% -m venv .venv || goto :fail
set "VPY=.venv\Scripts\python.exe"

echo ==^> Installo le dipendenze (qualche minuto)
"%VPY%" -m pip install -q -U pip || goto :fail
"%VPY%" -m pip install -r requirements.txt || goto :fail

rem le librerie native richiedono il runtime Visual C++, di solito gia' presente
"%VPY%" -c "import faster_whisper, sherpa_onnx" >nul 2>nul && goto :models
echo.
echo Manca il runtime Microsoft Visual C++ (serve alle librerie di trascrizione).
where winget >nul 2>nul || goto :novcredist
choice /c SN /m "Vuoi installarlo adesso (tramite winget)"
if errorlevel 2 goto :novcredist
winget install -e --id Microsoft.VCRedist.2015+.x64 --accept-package-agreements --accept-source-agreements
"%VPY%" -c "import faster_whisper, sherpa_onnx" >nul 2>nul && goto :models
:novcredist
echo Installa "Microsoft Visual C++ Redistributable x64" da
echo https://aka.ms/vs/17/release/vc_redist.x64.exe e rifai doppio click su setup.bat.
pause
exit /b 1

:models
echo ==^> Scarico i modelli (una volta sola)
"%VPY%" download_models.py || goto :fail

echo.
echo Pronto. Per l'uso quotidiano: doppio click su start.bat
echo.
pause
exit /b 0

:fail
echo.
echo Qualcosa e' andato storto: leggi il messaggio sopra.
pause
exit /b 1
