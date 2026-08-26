"""tests/test_meta_dynamics.py

Testy jednostkowe + integracyjny dla timdr_meta_dynamics.

Konwencja jak w innych projektach TIMDR w tym środowisku: sprawdzamy nie
tylko "działa na happy path", ale i konkretne bugi, które faktycznie
znalazłem w oryginalnym repo (brakujące importy, złe sygnatury,
brakująca metoda, twardy crash na starcie main.py).
"""
from __future__ import annotations

import math

import pytest

from core_meta.meta_state import MetaState
from core_meta.meta_time import MetaTime
from core_meta.meta_operator_M import MetaOperatorM
from models.evolution_field import FieldEvolution
from models.evolution_helix import HelixEvolution
from models.evolution_defect import DefectEvolution
from analysis.meta_map import MetaMap
from analysis.meta_predict import MetaPredict
from visualization.meta_phase_diagram import MetaPhaseDiagram

import main as main_module


# ---------------------------------------------------------------
# MetaState
# ---------------------------------------------------------------
def test_meta_state_delta():
    s1 = MetaState(Lambda=1.0, tau=2.0, rho=3.0, J=4.0)
    s2 = MetaState(Lambda=2.0, tau=2.0, rho=1.0, J=10.0)
    d = s1.delta(s2)
    assert d.Lambda == 1.0
    assert d.tau == 0.0
    assert d.rho == -2.0
    assert d.J == 6.0


# ---------------------------------------------------------------
# MetaTime
# ---------------------------------------------------------------
def test_meta_time_compute_i_normalize():
    mt = MetaTime()
    delta = MetaState(Lambda=1.0, tau=-2.0, rho=3.0, J=-4.0)
    val = mt.compute(delta)
    assert val == 10.0  # |1|+|2|+|3|+|4|
    norm = mt.normalize(val)
    assert 0.0 < norm < 1.0
    assert norm == pytest.approx(10.0 / 11.0)


def test_meta_time_normalize_zero():
    mt = MetaTime()
    assert mt.normalize(0.0) == 0.0


# ---------------------------------------------------------------
# MetaOperatorM
# ---------------------------------------------------------------
def test_meta_operator_compute():
    op = MetaOperatorM()
    s1 = MetaState(Lambda=0.0, tau=0.0, rho=0.0, J=0.0)
    s2 = MetaState(Lambda=2.0, tau=4.0, rho=-2.0, J=0.0)
    M = op.compute(s1, s2, dt=2.0)
    assert M.Lambda == 1.0
    assert M.tau == 2.0
    assert M.rho == -1.0
    assert M.J == 0.0


def test_meta_operator_compute_dt_zero_raises():
    # NAPRAWIONE: oryginal dzielil przez dt bez zabezpieczenia (ZeroDivisionError
    # zamiast czytelnego bledu) - test pilnuje, zeby zostalo to jawnym ValueError.
    op = MetaOperatorM()
    s1 = MetaState(0, 0, 0, 0)
    s2 = MetaState(1, 1, 1, 1)
    with pytest.raises(ValueError):
        op.compute(s1, s2, dt=0)


@pytest.mark.parametrize(
    "magnitude_state,expected",
    [
        (MetaState(0.01, 0.01, 0.01, 0.01), "stabilna"),      # suma 0.04 < 0.1
        (MetaState(0.1, 0.1, 0.1, 0.1), "przejsciowa"),        # suma 0.4, w [0.1,1.0)
        (MetaState(1.0, 1.0, 1.0, 1.0), "krytyczna"),          # suma 4.0 >= 1.0
    ],
)
def test_meta_operator_classify_phase_progi(magnitude_state, expected):
    op = MetaOperatorM()
    assert op.classify_phase(magnitude_state) == expected


def test_meta_operator_magnitude():
    op = MetaOperatorM()
    m = MetaState(Lambda=-1.0, tau=2.0, rho=-3.0, J=4.0)
    assert op.magnitude(m) == 10.0


# ---------------------------------------------------------------
# FieldEvolution - NAPRAWIONA sygnatura (konstruktor przyjmuje operator)
# ---------------------------------------------------------------
def test_field_evolution_simulate_uzywa_konstruktora():
    op = MetaOperatorM()
    fe = FieldEvolution(op)  # to jest DOKLADNIE to, jak wywoluje main.py
    states = [
        MetaState(0, 0, 0, 0),
        MetaState(1, 1, 1, 1),
        MetaState(3, 3, 3, 3),
    ]
    M_series = fe.simulate(states, dt=1.0)
    assert len(M_series) == 2
    assert M_series[0].Lambda == 1.0
    assert M_series[1].Lambda == 2.0


def test_field_evolution_pusta_i_jednoelementowa_seria():
    fe = FieldEvolution(MetaOperatorM())
    assert fe.simulate([], dt=1.0) == []
    assert fe.simulate([MetaState(0, 0, 0, 0)], dt=1.0) == []


# ---------------------------------------------------------------
# HelixEvolution / DefectEvolution
# ---------------------------------------------------------------
def test_helix_evolution_track():
    he = HelixEvolution()
    states = [
        MetaState(0, 0.1, 0, 0),   # narodziny
        MetaState(0, 0.5, 0, 0),   # stabilizacja
        MetaState(0, 1.5, 0, 0),   # rozpad
    ]
    assert he.track(states) == ["narodziny", "stabilizacja", "rozpad"]


def test_defect_evolution_track():
    de = DefectEvolution()
    states = [
        MetaState(0, 0, 0.1, 0),   # lokalna anomalia
        MetaState(0, 0, 0.5, 0),   # rozszerzajaca sie anomalia
        MetaState(0, 0, 2.0, 0),   # globalny defekt
    ]
    assert de.track(states) == [
        "lokalna anomalia",
        "rozszerzajaca sie anomalia",
        "globalny defekt",
    ]


# ---------------------------------------------------------------
# MetaMap - NAPRAWIONY konstruktor (przyjmuje meta_operator, jak main.py wymaga)
# ---------------------------------------------------------------
def test_meta_map_konstruktor_i_build():
    op = MetaOperatorM()
    mm = MetaMap(op)  # main.py: MetaMap(meta_operator) - musi dzialac
    states = [MetaState(0, 0, 0, 0)]
    M_series = [MetaState(0.05, 0.05, 0, 0)]
    data = mm.build(states, M_series)
    assert data["states"] == states
    assert data["meta_operator"] == M_series


def test_meta_map_detect_transitions():
    op = MetaOperatorM()
    mm = MetaMap(op)
    M_series = [
        MetaState(0.01, 0.01, 0.01, 0.01),   # stabilna
        MetaState(1.0, 1.0, 1.0, 1.0),        # krytyczna
    ]
    assert mm.detect_transitions(M_series) == ["stabilna", "krytyczna"]


# ---------------------------------------------------------------
# MetaPredict - DODANA simulate_future() (nie istniala w oryginale)
# ---------------------------------------------------------------
def test_meta_predict_predict_next():
    mp = MetaPredict()
    s = MetaState(0, 0, 0, 0)
    M = MetaState(1, 2, 3, 4)
    nxt = mp.predict_next(s, M, dt=2.0)
    assert nxt.Lambda == 2.0
    assert nxt.tau == 4.0
    assert nxt.rho == 6.0
    assert nxt.J == 8.0


def test_meta_predict_simulate_future_dlugosc_i_kumulacja():
    mp = MetaPredict()
    s0 = MetaState(0, 0, 0, 0)
    M_series = [MetaState(1, 0, 0, 0), MetaState(1, 0, 0, 0), MetaState(1, 0, 0, 0)]
    future = mp.simulate_future(s0, M_series, dt=1.0)
    # dlugosc = 1 (stan startowy) + len(M_series)
    assert len(future) == 4
    # kazdy kolejny stan powinien narastac (kumulacja, nie powrot do s0)
    assert [s.Lambda for s in future] == [0.0, 1.0, 2.0, 3.0]


def test_meta_predict_simulate_future_pusta_seria():
    mp = MetaPredict()
    s0 = MetaState(1, 1, 1, 1)
    future = mp.simulate_future(s0, [], dt=1.0)
    assert future == [s0]


# ---------------------------------------------------------------
# MetaPhaseDiagram - tylko sprawdzamy, ze nie crashuje (wersja tekstowa)
# ---------------------------------------------------------------
def test_meta_phase_diagram_plot_nie_crashuje(capsys):
    diag = MetaPhaseDiagram()
    diag.plot(["stabilna", "krytyczna"])
    captured = capsys.readouterr()
    assert "0: stabilna" in captured.out
    assert "1: krytyczna" in captured.out


# ---------------------------------------------------------------
# main.py - integracyjne: demo fallback + pelny pipeline
# ---------------------------------------------------------------
def test_load_demo_series_ksztalt_i_dlugosc():
    series = main_module.load_demo_series(n=20)
    assert len(series) == 20
    for point in series:
        assert set(point.keys()) == {"price", "volume", "trm", "flow"}
        assert all(math.isfinite(v) for v in point.values())


def test_build_meta_states_from_market_mapowanie():
    series = [{"price": 1.0, "trm": 2.0, "flow": 3.0, "volume": 4.0}]
    states = main_module.build_meta_states_from_market(series)
    assert len(states) == 1
    s = states[0]
    assert (s.Lambda, s.tau, s.rho, s.J) == (1.0, 2.0, 3.0, 4.0)


def test_run_meta_analysis_pelny_pipeline_z_demo_seria():
    # NAJWAZNIEJSZY test: caly pipeline main.py dziala end-to-end
    # BEZ analizator3_core (ktorego nie ma w tym repo) - to bylo
    # calkowicie zepsute w oryginale (ModuleNotFoundError na starcie).
    result = main_module.run_meta_analysis(series=main_module.load_demo_series(n=30))

    assert len(result["states"]) == 30
    assert len(result["M_series"]) == 29
    assert len(result["phases"]) == 29
    assert all(p in ("stabilna", "przejsciowa", "krytyczna") for p in result["phases"])
    # wstrzykniety skok w load_demo_series() powinien wywolac przynajmniej
    # jedna nie-stabilna faze - inaczej caly test danych demo bylby jalowy
    assert any(p != "stabilna" for p in result["phases"])
    assert len(result["future_states"]) >= 1


def test_run_meta_analysis_za_krotka_seria_rzuca_czytelny_blad():
    with pytest.raises(ValueError):
        main_module.run_meta_analysis(series=[{"price": 1, "trm": 1, "flow": 1, "volume": 1}])


def test_run_meta_analysis_bez_analizator3_core_uzywa_demo(monkeypatch, capsys):
    # Potwierdza realne zachowanie z main.py: gdy series=None i
    # analizator3_core nie jest zainstalowany (co jest prawda w tym
    # srodowisku testowym), pipeline i tak dziala, a nie wywala ImportError.
    result = main_module.run_meta_analysis()
    captured = capsys.readouterr()
    assert "[UWAGA]" in captured.out
    assert len(result["states"]) > 0
