"""models/evolution_field.py

Ewolucja globalnego pola TIMDR: seria M-stanów licznona z serii S-stanów.

NAPRAWIONE: oryginalna sygnatura `simulate(self, states, meta_operator, dt)`
nie zgadzała się z tym, jak main.py faktycznie wywołuje tę klasę:

    field_evolution = FieldEvolution(meta_operator)
    M_series = field_evolution.simulate(states, dt)

main.py przekazuje meta_operator do KONSTRUKTORA, nie do simulate() -
oryginalny plik w tej postaci wywalałby TypeError przy pierwszym użyciu
z main.py. Sygnatura poprawiona, żeby faktycznie pasowała do main.py
(to samo API, co miał już wcześniej sam plik timdr_meta_dynamics/__init__.py -
main.py był pisany pod TĘ wersję, nie pod oryginalny models/evolution_field.py).
"""
from __future__ import annotations

from typing import List

from core_meta.meta_state import MetaState
from core_meta.meta_operator_M import MetaOperatorM


class FieldEvolution:
    """Ewolucja globalnego pola TIMDR."""

    def __init__(self, meta_operator: MetaOperatorM):
        self.meta_operator = meta_operator

    def simulate(self, states: List[MetaState], dt: float) -> List[MetaState]:
        M_series: List[MetaState] = []

        for i in range(len(states) - 1):
            M = self.meta_operator.compute(states[i], states[i + 1], dt)
            M_series.append(M)

        return M_series
