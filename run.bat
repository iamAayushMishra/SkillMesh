@echo off
cd /d "%~dp0"
echo ============================================================
echo Starting SkillMesh Semantic Web Server...
echo URL: http://127.0.0.1:5000
echo ============================================================
call .venv\Scripts\python.exe app.py
pause
