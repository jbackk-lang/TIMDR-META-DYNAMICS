# analysis/meta_trigger.py
"""
Zamiana sekwencji etykiet fazy PER KROK w JEDNO zdarzenie punktowe.

POWÓD ISTNIENIA TEGO PLIKU: MetaMap.detect_transitions() i
DefectEvolution.track() zwracają listę faz - jedną etykietę na KAŻDY
krok M-serii, nie momenty ZMIANY fazy (patrz ich własne docstringi:
"to NIE jest wykrywanie przejść w sensie punktowym", "nazwa metody
sugeruje coś bardziej wyrafinowanego niż faktyczna implementacja").
main.py::run_meta_analysis() zwraca tę surową listę w wyniku
("phases"), ale nic w repo nie odpowiada na pytanie "w KTÓRYM kroku
pole PIERWSZY RAZ wpadło w najpoważniejszy monitorowany stan" - to
jest właśnie robota tego dispatchera. Nie liczy własnej statystyki,
tylko interpretuje już obliczoną listę etykiet.
"""
from __future__ import annotations

from typing import List, Optional, Sequence


class MetaTriggerResult:
    def __init__(self, triggered: bool = False, trigger_type: str = "none",
                 location: Optional[int] = None, message: str = ""):
        self.triggered = triggered
        self.trigger_type = trigger_type
        self.location = location
        self.message = message

    def as_dict(self) -> dict:
        return {
            "triggered": self.triggered,
            "type": self.trigger_type,
            "location": self.location,
            "message": self.message,
        }


class MetaTrigger:
    """
    Dispatcher nad sekwencją etykiet fazy (lista stringów, jedna faza na
    krok). Priorytet zadawany przez `severity_order` (od
    NAJPOWAZNIEJSZEJ do najlżejszej) - zwraca pierwszy krok, w którym
    pole osiągnęło NAJPOWAZNIEJSZY z monitorowanych poziomów, gdziekolwiek
    on wystąpił w serii (nie tylko na końcu).

    Domyślnie skonfigurowany pod MetaMap.detect_transitions()
    ("stabilna"/"przejsciowa"/"krytyczna" - patrz MetaOperatorM.
    classify_phase()). Dla DefectEvolution.track() ("lokalna anomalia"/
    "rozszerzajaca sie anomalia"/"globalny defekt") podaj własny
    severity_order:

        MetaTrigger(severity_order=("globalny defekt",
                                     "rozszerzajaca sie anomalia",
                                     "lokalna anomalia"))

    Świadomie NIE używa jednego wspólnego Enuma dla `trigger_type` -
    ten repo ma dwie NIEZALEŻNE, heterogeniczne słowniki faz
    (MetaOperatorM vs DefectEvolution), więc `trigger_type` jest po
    prostu jedną z etykiet podanych w `severity_order` (albo "none").
    """

    DEFAULT_SEVERITY_ORDER = ("krytyczna", "przejsciowa")

    def __init__(self, severity_order: Optional[Sequence[str]] = None):
        self.severity_order = tuple(severity_order) if severity_order else self.DEFAULT_SEVERITY_ORDER
        self.last_result = MetaTriggerResult()

    def analyze(self, phases: List[str]) -> MetaTriggerResult:
        for label in self.severity_order:
            for i, phase in enumerate(phases):
                if phase == label:
                    return self._set_result(
                        True, label, i,
                        f"Faza '{label}' osiągnięta pierwszy raz w kroku {i}."
                    )
        return self._set_result(
            False, "none", None,
            "Żaden z monitorowanych poziomów nie został osiągnięty w całej serii."
        )

    def _set_result(self, triggered, trigger_type, location, message):
        self.last_result = MetaTriggerResult(triggered, trigger_type, location, message)
        return self.last_result

    def get_last(self) -> MetaTriggerResult:
        return self.last_result
