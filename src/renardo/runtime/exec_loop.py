"""
Renardo exec loop — subprocess d'exécution de code.

Lit des blocs de code depuis stdin, chacun terminé par la ligne sentinelle
__EXEC_END__, et les exécute via exec() dans un namespace contrôlé.

Avantages vs `python -i` (REPL interactif) :
- Pas de mise à jour automatique de `_` par le REPL (la variable rest/silence
  n'est jamais corrompue par les expressions comme `p >> instrument(...)`)
- Les blocs multi-lignes avec boucles/conditions n'ont pas besoin de lignes
  vides supplémentaires pour être acceptés
- Le namespace persiste entre les exécutions (même comportement que l'ancien
  éditeur FoxDot basé sur exec())
"""
import sys
import traceback

# --- Bootstrap : importer tout le runtime renardo dans ce namespace ---
from renardo.runtime import *  # noqa: F401, F403

# Snapshot du namespace AVANT les variables de contrôle de boucle.
# dict() crée une copie superficielle : les objets mutables (Clock, Server…)
# sont partagés par référence, donc les mutations du code utilisateur se propagent.
_exec_ns = dict(globals())
_exec_ns['_'] = None  # garantit que _ commence comme marqueur de silence

# Variables de contrôle — assignées après le snapshot, non visibles dans _exec_ns
_SENTINEL = "__EXEC_END__"
_buf = []

sys.stdout.write("Renardo exec loop ready\n")
sys.stdout.flush()

for _ln in sys.stdin:
    _ln = _ln.rstrip('\n')
    if _ln == _SENTINEL:
        _code = '\n'.join(_buf)
        _buf = []
        if _code.strip():
            try:
                exec(compile(_code, "<renardo>", "exec"), _exec_ns)
            except SystemExit:
                pass  # ne pas laisser sys.exit() tuer la boucle
            except Exception:
                traceback.print_exc(file=sys.stderr)
            finally:
                sys.stdout.flush()
                sys.stderr.flush()
    else:
        _buf.append(_ln)
