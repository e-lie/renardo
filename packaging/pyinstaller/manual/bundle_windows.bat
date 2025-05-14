echo off

:: lolilolilolilol le BAT
::for %%i in ("%CD%\..") do set "PARENT_DIR=%%~fi"

set "VENV_DIR=%userprofile%\Desktop\venv_pyinstaller"

@RD /S /Q "%VENV_DIR%"

set "RENARDO_VERSION=1.0.0.dev23"

python -m venv %VENV_DIR%

CALL %VENV_DIR%\Scripts\activate.bat

:: fix playsound install https://stackoverflow.com/questions/76142067/on-github-actions-pip-install-playsound-failed-with-the-oserror-could-not-g
pip install --upgrade setuptools wheel

cd ..
cd ..
pip install --upgrade --no-cache-dir renardo==%RENARDO_VERSION%
pip install --no-cache-dir -r requirements.pyinstaller.txt

cd builder

::python -m PyInstaller renardo_bundle.py --collect-all renardo --collect-all FoxDotEditor --collect-all renardo_sitter --hidden-import wave --hidden-import psutil --hidden-import json --hidden-import queue --hidden-import socketserver --hidden-import tkinter --clean
python -m PyInstaller "renardo-entrypoint.py" ^
--name "renardo-%RENARDO_VERSION%" ^
--collect-all renardo ^
--collect-all FoxDotEditor ^
--collect-all renardo_lib ^
--collect-all renardo.gatherer ^
--collect-all textual ^
--noconfirm ^
--distpath "%userprofile%\Desktop\renardo-%RENARDO_VERSION%" ^
--workpath "%userprofile%\Desktop\renardo_pyinstaller_build" ^
--clean


::--onefile prevent usage with pulsar ?
::--onefile ^ 

set "sourceFolder=%userprofile%\Desktop\renardo-%RENARDO_VERSION%\renardo-%RENARDO_VERSION%"
set "destinationZip=%userprofile%\Desktop\renardo-%RENARDO_VERSION%-windows.zip"

PowerShell -Command "Compress-Archive -Path '%sourceFolder%' -DestinationPath '%destinationZip%'"
