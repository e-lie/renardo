@echo off

:: lolilolilolilol le BAT
for %%i in ("%CD%\..") do set "PARENT_DIR=%%~fi"

set "VENV_DIR=%PARENT_DIR%\venv"

set "RENARDO_VERSION=0.9.3rc"

python -m venv %VENV_DIR%

CALL %VENV_DIR%\Scripts\activate.bat

:: fix playsound install https://stackoverflow.com/questions/76142067/on-github-actions-pip-install-playsound-failed-with-the-oserror-could-not-g
pip install --upgrade setuptools wheel

cd ..
pip install -r requirements.pyinstaller.txt

cd pyinstaller_bundle

::python -m PyInstaller renardo_bundle.py --collect-all renardo --collect-all FoxDotEditor --collect-all renardo_sitter --hidden-import wave --hidden-import psutil --hidden-import json --hidden-import queue --hidden-import socketserver --hidden-import tkinter --clean
python -m PyInstaller "renardo-entrypoint.py" ^
--collect-all renardo ^
--collect-all FoxDotEditor ^
--collect-all renardo_lib ^
--collect-all renardo_gatherer ^
--collect-all textual ^
--noconfirm ^
--distpath "C:\User\Desktop\renardo-%RENARDO_VERSION%"
--workpath "C:\User\Desktop\renardo_pyinstaller_build"
--clean


::--onefile prevent usage with pulsar ?
::--onefile ^ 

set "sourceFolder=C:\User\Desktop\renardo-%RENARDO_VERSION%\renardo-%RENARDO_VERSION%"
set "destinationZip=C:\User\Desktop\renardo-%RENARDO_VERSION%.zip"

PowerShell -Command "Compress-Archive -Path '%sourceFolder%' -DestinationPath '%destinationZip%'"
