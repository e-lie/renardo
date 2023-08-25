
```bash
python3 -m build --wheel .   # a lancer hors venv
twine upload -r testpypi dist/* --verbose
```