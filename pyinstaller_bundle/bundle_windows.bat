::Set-ExecutionPolicy Unrestricted -Scope Process
::pip uninstall renardo renardo_sitter FoxDotEditor pyinstaller wave psutil

git clone https://github.com/e-lie/renardo.git ../renardo
git clone https://github.com/e-lie/FoxDotEditor.git ../FoxDotEditor
git clone https://github.com/e-lie/renardo_sitter.git ../renardo_sitter

python -m venv venv

.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip list

:: python -m PyInstaller renardo_bundle.py --collect-all renardo --collect-all FoxDotEditor --collect-all renardo_sitter --hidden-import wave --hidden-import psutil --hidden-import json --hidden-import queue --hidden-import socketserver --hidden-import tkinter --clean
python -m PyInstaller renardo_bundle.py --collect-all renardo --collect-all FoxDotEditor --collect-all renardo_sitter --hidden-import wave --hidden-import psutil --clean