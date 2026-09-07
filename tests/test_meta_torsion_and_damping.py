"""tests/test_meta_torsion_and_damping.py

Testy dla dwoch dodatkow dorobionych po analizie repo "w swietle
ostatnich doswiadczen" z FLIGHT-TRACKING-TIMDR:

1. analysis/meta_torsion.field_torsion() - prawdziwa krzywizna/torsja
   Freneta-Serreta trajektorii (Λ, τ, ρ), zweryfikowana na helisie
   kolowej z zamknietym wzorem (ten sam wzorzec testu co
   test_frenet_serret_helisa we FLIGHT-TRACKING-TIMDR).
2. analysis/meta_predict.MetaPredict.simulate_future(damping=...) -
   tlumienie ekstrapolacji Eulera w strone kotwicy (current_state).
"""
import numpy as np
import pytest

from core_meta.meta_state import MetaState
from analysis.meta_torsion import field_torsion
from analysis.meta_predict import MetaPredict


# ---------------------------------------------------------------
# field_torsion
# ---------------------------------------------------------------

def _helisa_stany(R=2.0, w=0.7, c=0.5, n=60, dt=0.05):
    """Stany MetaState, gdzie (Λ, τ, ρ) = (R cos(w t), R sin(w t), c t) -
    czysta helisa kolowa o znanej, zamknietej krzywiznie/torsji.
    J jest tu nieuzywane (nie wchodzi do trajektorii 3D) - ustawione na 0.
    """
    ts = np.arange(n) * dt
    states = [
        MetaState(Lambda=R * np.cos(w * t), tau=R * np.sin(w * t), rho=c * t, J=0.0)
        for t in ts
    ]
    return states, dt


def test_field_torsion_helisa_kolowa_zgadza_sie_ze_wzorem_zamknietym():
    R, w, c = 2.0, 0.7, 0.5
    states, dt = _helisa_stany(R=R, w=w, c=c)

    kappa, tors = field_torsion(states, dt=dt)

    kappa_oczek = R * w**2 / (R**2 * w**2 + c**2)
    tau_oczek = c * w / (R**2 * w**2 + c**2)

    # srodkowy fragment (z dala od brzegow okna wygladzania)
    srodek = slice(15, -15)
    assert np.allclose(kappa[srodek], kappa_oczek, rtol=2e-2)
    assert np.allclose(tors[srodek], tau_oczek, rtol=2e-2)


def test_field_torsion_krotka_seria_zwraca_zera_zamiast_wyjatku():
    states = [MetaState(0, 0, 0, 0), MetaState(1, 1, 1, 1)]
    kappa, tors = field_torsion(states, dt=1.0)
    assert len(kappa) == len(tors) == 2
    assert np.all(kappa == 0.0)
    assert np.all(tors == 0.0)


def test_field_torsion_nie_nadpisuje_pola_tau_wejsciowego():
    """field_torsion() to osobna funkcja zwracajaca nowe tablice - stany
    wejsciowe (i ich .tau) musza zostac nietkniete."""
    states, dt = _helisa_stany(n=20)
    tau_przed = [s.tau for s in states]
    field_torsion(states, dt=dt)
    tau_po = [s.tau for s in states]
    assert tau_przed == tau_po


# ---------------------------------------------------------------
# MetaPredict.simulate_future(damping=...)
# ---------------------------------------------------------------

def test_simulate_future_domyslny_damping_1_0_zachowuje_stare_zachowanie():
    """damping domyslnie 1.0 -> dokladnie stara, nietlumiona kumulacja
    (regresja: to samo co test_meta_predict_simulate_future_dlugosc_i_kumulacja
    w test_meta_dynamics.py, powtorzone tutaj dla jasnosci kontraktu)."""
    mp = MetaPredict()
    s0 = MetaState(0, 0, 0, 0)
    M_series = [MetaState(1, 0, 0, 0)] * 5
    future = mp.simulate_future(s0, M_series, dt=1.0)
    assert [s.Lambda for s in future] == [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]


def test_simulate_future_z_tlumieniem_jest_ograniczone():
    """damping < 1.0: dla stalego M, kumulacja Eulera E rosnie liniowo bez
    granic, ale wynik po tlumieniu jest ograniczony (zbiega do stalej
    wartosci granicznej current_state + M*dt*damping/(1-damping) dla
    dlugiego horyzontu), zamiast rosnac w nieskonczonosc."""
    mp = MetaPredict()
    s0 = MetaState(0, 0, 0, 0)
    M_series = [MetaState(1, 0, 0, 0)] * 200
    future = mp.simulate_future(s0, M_series, dt=1.0, damping=0.85)
    wartosci = [s.Lambda for s in future]

    # rosnie na poczatku...
    assert wartosci[5] > wartosci[1]
    # ...ale nie rosnie bez ograniczen - stabilizuje sie (ostatnie kroki
    # niemal identyczne), w przeciwienstwie do niedlumionej wersji ktora
    # po 200 krokach dalaby 200.0
    assert abs(wartosci[-1] - wartosci[-2]) < 1e-6
    assert wartosci[-1] < 10.0  # daleko od nietlumionej wartosci 200.0


def test_simulate_future_damping_mniej_tlumi_niz_wiecej_dla_tego_samego_kroku():
    mp = MetaPredict()
    s0 = MetaState(0, 0, 0, 0)
    M_series = [MetaState(1, 0, 0, 0)] * 10
    luzne = mp.simulate_future(s0, M_series, dt=1.0, damping=0.95)
    silne = mp.simulate_future(s0, M_series, dt=1.0, damping=0.7)
    assert luzne[-1].Lambda > silne[-1].Lambda


def test_simulate_future_pusta_seria_dziala_z_damping():
    mp = MetaPredict()
    s0 = MetaState(1, 1, 1, 1)
    future = mp.simulate_future(s0, [], dt=1.0, damping=0.85)
    assert future == [s0]
