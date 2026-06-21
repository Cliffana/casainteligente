@echo off
echo Starting Casa Inteligente preview server...
echo Open: http://localhost:8006
cd /d "%~dp0output"
python -m http.server 8006
pause
