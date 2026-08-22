"""analysis/meta_map.py

Mapa zmian pola w czasie + wykrywanie globalnych przejść fazowych.

NAPRAWIONE (dwa błędy):
1. Oryginał nie importował MetaOperatorM (NameError przy realnym użyciu
   poza timdr_meta_dynamics/__init__.py, gdzie wszystko siedziało w
   jednym pliku).
2. `MetaMap` w oryginale nie miał __init__ (klasa bezargumentowa), ale
   main.py wywołuje `MetaMap(meta_operator)` - TypeError: MetaMap()
   takes no arguments. Dodany konstruktor przyjmujący meta_operator,
   używany potem w detect_transitions() zamiast tworzenia nowej
   instancji MetaOperatorM() przy każdym wywołaniu (co i tak działało
   przypadkiem, bo MetaOperatorM jest bezstanowy, ale było niespójne
   z resztą kodu, gdzie operator jest wstrzykiwany, nie tworzony
   lokalnie).
"""
from __future__ import annotations

from typing import List

from core_meta.meta_state import MetaState
from core_meta.meta_operator_M import MetaOperatorM


class MetaMap:
    """Mapa zmian pola w czasie."""

    def __init__(self, meta_operator: MetaOperatorM):
        self.meta_operator = meta_operator

    def build(self, states: List[MetaState], M_series: List[MetaState]) -> dict:
        return {
            "states": states,
            "meta_operator": M_series,
        }

    def detect_transitions(self, M_series: List[MetaState]) -> List[str]:
        """Zwraca listę faz (stabilna/przejsciowa/krytyczna) per krok M-serii.

        UWAGA: to NIE jest "wykrywanie przejść" w sensie punktowym (tj.
        nie zwraca tylko momentów ZMIANY fazy) - zwraca fazę dla KAŻDEGO
        kroku, tak jak robił to oryginał. Nazwa metody (detect_transitions)
        sugeruje coś bardziej wyrafinowanego niż faktyczna implementacja -
        zaznaczone tu wprost, żeby nazwa nie wprowadzała w błąd.
        """
        transitions: List[str] = []

        for M in M_series:
            phase = self.meta_operator.classify_phase(M)
            transitions.append(phase)

        return transitions
