@echo off

:: lolilolilolilol le BAT
for %%i in ("%CD%\..") do set "PARENT_DIR=%%~fi"

set "VENV_DIR=%PARENT_DIR%\venv"

set "RENARDO_VERSION=0.9.3"

python -m venv %VENV_DIR%

CALL %VENV_DIR%\Scripts\activate.bat

:: fix playsound install https://stackoverflow.com/questions/76142067/on-github-actions-pip-install-playsound-failed-with-the-oserror-could-not-g
pip install --upgrade setuptools wheel

cd ..
pip install -r requirements.pyinstaller.txt

cd pyinstaller_bundle

::python -m PyInstaller renardo_bundle.py --collect-all renardo --collect-all FoxDotEditor --collect-all renardo_sitter --hidden-import wave --hidden-import psutil --hidden-import json --hidden-import queue --hidden-import socketserver --hidden-import tkinter --clean
python -m PyInstaller "renardo-%RENARDO_VERSION%.py" ^
--collect-all renardo ^
--collect-all FoxDotEditor ^
--collect-all renardo_lib ^
--collect-all renardo_gatherer ^
--collect-all textual ^
--noconfirm ^
--clean


::--onefile prevent usage with pulsar ?
::--onefile ^ 