@echo off
cd /d "C:\opencode_file\v2\site-casa-inteligente\output"
echo Starting server at http://localhost:8006
echo Press CTRL+C to stop
python -m http.server 8006
pause
