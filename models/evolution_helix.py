"""models/evolution_helix.py

Ewolucja helis: narodziny / stabilizacja / rozpad, na podstawie τ (tau).

Self-contained (nie konstruuje MetaState, tylko czyta atrybut .tau) -
działał już poprawnie w oryginale, bez zmian poza dodaniem type hints
i jawnego importu MetaState (dla czytelności sygnatury, nie dla
poprawności działania).

UWAGA o progach: 0.2 i 1.0 to arbitralne wartości ze szkicu, tak samo
jak w MetaOperatorM.classify_phase() - do skalibrowania na realnych
danych przed użyciem produkcyjnym.
"""
from __future__ import annotations

from typing import List

from core_meta.meta_state import MetaState


class HelixEvolution:
    """Ewolucja helis: narodziny, stabilizacja, rozpad."""

    def track(self, helix_states: List[MetaState]) -> List[str]:
        lifecycle: List[str] = []

        for state in helix_states:
            if state.tau < 0.2:
                lifecycle.append("narodziny")
            elif state.tau < 1.0:
                lifecycle.append("stabilizacja")
            else:
                lifecycle.append("rozpad")

        return lifecycle
