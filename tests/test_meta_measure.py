"""
tests/test_meta_measure.py -- mierzalne tau, rho i rezim (analysis/meta_measure.py).

Wartosci wzorcowe policzone implementacja walidowana GIA-TIMDR core/transition_params.py na tym samym sygnale
(zgodnosc bit w bit sprawdzona przy przenoszeniu, 2026-09-27).
"""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from analysis.meta_measure import (band_envelope, event_density, feasibility, measure, measured_state, n_cycles,
                                   regime, relative_to_background)
from core_meta.meta_state import MetaState

FS = 20000.0


def _impulses(rate, tau, n=40000, seed=3):
    """Gasnace impulsy 3 kHz (czas wygaszania tau) w czasach Poissona o czestosci rate + slaby szum."""
    rng = np.random.default_rng(seed); x = np.zeros(n)
    times = np.cumsum(rng.exponential(1 / rate, int(rate * n / FS * 2) + 10)); times = times[times < n / FS]
    for t0 in times:
        i = int(t0 * FS); L = min(n - i, int(10 * tau * FS)); tt = np.arange(L) / FS
        x[i:i + L] += np.exp(-tt / tau) * np.sin(2 * np.pi * 3000 * tt)
    return x + 0.01 * rng.standard_normal(n)


def test_event_density_golden():
    e = band_envelope(_impulses(100, 0.001), FS, 1000, 6000)
    d = event_density(e, FS)
    assert d["D"] == pytest.approx(0.250458, abs=1e-6)
    assert d["eta"] == pytest.approx(0.200293, abs=1e-6)
    assert d["tau"] == pytest.approx(0.00105, abs=1e-12)


def test_rho_grows_with_rate_times_tau_and_regimes():
    rhos = [measure(_impulses(r, t), FS, 1000, 6000)["rho"] for r, t in [(20, 0.001), (100, 0.001), (1000, 0.002)]]
    assert rhos[0] < rhos[1] < rhos[2]
    assert [regime(r) for r in rhos] == ["czasteczka", "czasteczka", "pakiet"]
    m = measure(_impulses(100, 0.001), FS, 1000, 6000)
    assert m["eta"] == pytest.approx(2 * 100 * 0.001, rel=0.05)     # rzadkie impulsy ponad szumem: eta ~ 2 f tau
    assert m["tau"] == pytest.approx(0.001, rel=0.1)                # czas wygaszania odzyskany


def test_gaussian_noise_is_wave():
    m = measure(np.random.default_rng(0).standard_normal(40000), FS, 1000, 6000)
    assert m["rezim"] == "fala" and m["rho"] == pytest.approx(3.63, abs=0.05)   # teoria dla szumu ~ 3,7


def test_relative_to_background_and_state():
    x = _impulses(100, 0.001); bg = measure(np.random.default_rng(0).standard_normal(40000), FS, 1000, 6000)["rho"]
    s = measured_state(x, FS, 1000, 6000, Lambda=1.0, J=2.0, rho_background=bg)
    assert isinstance(s, MetaState) and s.Lambda == 1.0 and s.J == 2.0
    assert s.rho == pytest.approx(relative_to_background(0.250458, bg), abs=1e-6) and s.rho < 1.0
    assert s.tau == pytest.approx(0.00105, abs=1e-12)


def test_feasibility_rule():
    r = feasibility(n_cycles(0.1, 50), 100, 0.1, "stala")          # 5 cykli: za malo
    assert r["sito_ma_szanse"] is False and r["reżim"] == "czasteczka"
    r = feasibility(n_cycles(1.0, 50), 20, 5.0, "sledzona")        # L_koh < N_cyk: prostowac rure
    assert r["sito_ma_szanse"] is True and any("wyprostowac" in p for p in r["droga"]) and r["reżim"] == "fala"
    assert feasibility(50, 100, 1.0, "wolna")["sito_ma_szanse"] is False
