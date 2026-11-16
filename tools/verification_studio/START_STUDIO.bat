@echo off
setlocal
cd /d "%~dp0"
python ETABS_OpenSees_Verification_Studio.py
if errorlevel 1 pause
endlocal
