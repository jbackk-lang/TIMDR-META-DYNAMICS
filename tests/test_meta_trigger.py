"""
tests/test_meta_trigger.py — testy analysis/meta_trigger.py (MetaTrigger).

1. test_krytyczna_na_realnym_detect_transitions - JEDEN test integracyjny
   na prawdziwym MetaMap.detect_transitions()/MetaOperatorM (bez
   mockowania), z ręcznie skonstruowaną M-serią o znanych magnitude
   (patrz MetaOperatorM.classify_phase(): <0.1 stabilna, <1.0 przejsciowa,
   >=1.0 krytyczna).
2. Reszta testów podaje RĘCZNIE zbudowane listy faz - testujemy
   WYŁĄCZNIE logikę dispatchera (pierwszy-najpoważniejszy, konfigurowalny
   severity_order dla DefectEvolution.track()).
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core_meta.meta_state import MetaState
from core_meta.meta_operator_M import MetaOperatorM
from analysis.meta_map import MetaMap
from analysis.meta_trigger import MetaTrigger


# ----------------------------------------------------------------------
# 1) Test integracyjny na realnym MetaMap/MetaOperatorM
# ----------------------------------------------------------------------

def test_krytyczna_na_realnym_detect_transitions():
    """
    M-seria (6 kroków) o ręcznie wybranych magnitude:
      0: (0,0,0,0)          magnitude=0.0    -> stabilna
      1: (0,0,0,0)          magnitude=0.0    -> stabilna
      2: (0.02,0.02,0.02,0.02) magnitude=0.08 -> stabilna (< 0.1)
      3: (0.1,0.1,0.1,0.1)  magnitude=0.4    -> przejsciowa
      4: (1.0,1.0,1.0,1.0)  magnitude=4.0    -> krytyczna
      5: (0,0,0,0)          magnitude=0.0    -> stabilna
    Oczekiwane phases = ["stabilna"]*3 + ["przejsciowa","krytyczna","stabilna"].
    MetaTrigger domyślny (severity_order=("krytyczna","przejsciowa"))
    znajduje "krytyczna" jako najpoważniejszą, pierwszy raz w indeksie 4 -
    niezależnie od tego, że "przejsciowa" wystąpiła wcześniej (indeks 3).
    """
    M_series = [
        MetaState(0.0, 0.0, 0.0, 0.0),
        MetaState(0.0, 0.0, 0.0, 0.0),
        MetaState(0.02, 0.02, 0.02, 0.02),
        MetaState(0.1, 0.1, 0.1, 0.1),
        MetaState(1.0, 1.0, 1.0, 1.0),
        MetaState(0.0, 0.0, 0.0, 0.0),
    ]
    meta_map = MetaMap(MetaOperatorM())
    phases = meta_map.detect_transitions(M_series)
    assert phases == ["stabilna", "stabilna", "stabilna", "przejsciowa", "krytyczna", "stabilna"]

    trigger = MetaTrigger()
    result = trigger.analyze(phases)

    assert result.triggered is True
    assert result.trigger_type == "krytyczna"
    assert result.location == 4


# ----------------------------------------------------------------------
# 2) Testy logiki dispatchera na ręcznie zbudowanych listach faz
# ----------------------------------------------------------------------

def test_przejsciowa_gdy_nigdy_nie_ma_krytycznej():
    phases = ["stabilna", "przejsciowa", "stabilna", "przejsciowa"]
    result = MetaTrigger().analyze(phases)
    assert result.triggered is True
    assert result.trigger_type == "przejsciowa"
    assert result.location == 1


def test_none_gdy_zawsze_stabilna():
    phases = ["stabilna"] * 5
    result = MetaTrigger().analyze(phases)
    assert result.triggered is False
    assert result.trigger_type == "none"
    assert result.location is None


def test_krytyczna_wygrywa_niezaleznie_od_pozycji_chronologicznej():
    """Krytyczna WCZESNIEJ w chronologii niz kolejna przejsciowa - i tak
    wygrywa krytyczna (priorytet po typie, nie po czasie), lokalizacja to
    JEJ wlasny (najwczesniejszy) indeks."""
    phases = ["przejsciowa", "krytyczna", "przejsciowa", "stabilna"]
    result = MetaTrigger().analyze(phases)
    assert result.trigger_type == "krytyczna"
    assert result.location == 1


def test_konfigurowalny_severity_order_dla_defect_evolution():
    """DefectEvolution.track() zwraca inny słownik etykiet - dispatcher
    musi działać identycznie po podaniu własnego severity_order."""
    phases = ["lokalna anomalia", "rozszerzajaca sie anomalia", "globalny defekt", "lokalna anomalia"]
    trigger = MetaTrigger(severity_order=(
        "globalny defekt", "rozszerzajaca sie anomalia", "lokalna anomalia",
    ))
    result = trigger.analyze(phases)
    assert result.trigger_type == "globalny defekt"
    assert result.location == 2


def test_get_last_zwraca_ostatni_wynik():
    trigger = MetaTrigger()
    result = trigger.analyze(["stabilna", "krytyczna"])
    assert trigger.get_last() is result
