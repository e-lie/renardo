
# Pyinstaller is intensely hacky to use

-> have faith and read the log output !!

# Config is

venv + editable_dev libraries + pyinstaller inside venv+-

# Scripting on windows is really shitty

Powershell refuses to switch to a venv without activating permission manually... https://stackoverflow.com/questions/18713086/virtualenv-wont-activate-on-windows

> Set-ExecutionPolicy Unrestricted -Scope Process
then > .\venv\Scripts\Activate.ps1
