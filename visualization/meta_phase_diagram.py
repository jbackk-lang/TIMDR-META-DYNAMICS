"""visualization/meta_phase_diagram.py

Diagram faz meta-pola.

UWAGA O NAZEWNICTWIE: mimo nazwy "diagram", to jest wersja WYŁĄCZNIE
tekstowa (drukuje listę faz do stdout) - nie generuje żadnego wykresu.
Tak było już w oryginale, zostawione bez zmian funkcjonalnych, ale
nazwane wprost tutaj, żeby nie sugerować czegoś, czego kod nie robi
(ten sam rodzaj zastrzeżenia, co np. przy MetaMap.detect_transitions()
w analysis/meta_map.py). Rzeczywisty wykres (3D, matplotlib) jest w
meta_flow_3d.py - ten plik jest osobny i faktycznie rysuje.
"""
from __future__ import annotations

from typing import List


class MetaPhaseDiagram:
    """Diagram faz meta-pola (wersja tekstowa)."""

    def plot(self, phases: List[str]) -> None:
        for i, phase in enumerate(phases):
            print(f"{i}: {phase}")
