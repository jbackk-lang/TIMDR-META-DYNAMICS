"""models/evolution_defect.py

Ewolucja defektów/anomalii pola TIMDR, na podstawie ρ (rho).

Self-contained, bez zmian funkcjonalnych względem oryginału - dodane
tylko type hints. Te same zastrzeżenia co do arbitralnych progów (0.3,
1.0), co w evolution_helix.py.
"""
from __future__ import annotations

from typing import List

from core_meta.meta_state import MetaState


class DefectEvolution:
    """Ewolucja defektów/anomalii w polu TIMDR."""

    def track(self, defect_states: List[MetaState]) -> List[str]:
        phases: List[str] = []

        for state in defect_states:
            if state.rho < 0.3:
                phases.append("lokalna anomalia")
            elif state.rho < 1.0:
                phases.append("rozszerzajaca sie anomalia")
            else:
                phases.append("globalny defekt")

        return phases
