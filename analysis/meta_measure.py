"""analysis/meta_measure.py

Mierzalne tau i rho stanu meta (S_meta = {Lambda, tau, rho, J}) z sygnalu -- zamiast wartosci wpisywanych recznie.

    tau -- czas wygaszania zdarzenia: autokorelacja obwiedni pasma spada ponizej 1/e [s]
    rho -- gestosc zdarzen D = eta / (1 - eta), eta = (E e)^2 / E(e^2) (wypelnienie obwiedni, bez progu);
           rosnie z f * tau (czestosc x czas wygaszania); dla rzadkich gasnacych impulsow ponad szumem eta ~ 2 f tau.
           Czestosc zdarzen 'rate' jest tylko pomocnicza -- liczenie maksimow zawodzi przy gestych zdarzeniach,
           dlatego rho mierzone jest wypelnieniem, nie zliczaniem
    rezim -- D < 0,3 czasteczka (rzadkie blyski), 0,3..3 pakiet, D > 3 fala (szum gaussowski D ~ 3,7)

Funkcje band_envelope, event_density, regime, n_cycles, feasibility przeniesione 1:1 (bez importu -- repo niezalezne)
z GIA-TIMDR core/transition_params.py; zgodnosc liczbowa pilnowana testem wzorcowym (tests/test_meta_measure.py).

Walidacja (pre-rejestrowana, GIA-TIMDR docs/geometry/):
  PRONOSTIA_REGIME_PATH_v0_1 -- 11 nieogladanych lozysk do zniszczenia: D spada wzdluz zycia w 9/11 (pole -> czasteczka),
      na koncu wraca >= 1,2 x minimum w 7/11 (ku fali) -- SUPPORTED; D zachowuje sie jak kurtoza (remis, nie przewaga).
  LANL_MODAL_ANCHOR_v0_3 H3 -- w ramie budynku przy szerokopasmowym wymuszeniu D NIE sledzilo ciezkosci -- NOT SUPPORTED.
  Wniosek: rho interpretowac WZGLEDEM TLA tej samej maszyny/konstrukcji (relative_to_background), nie jako liczbe
  bezwzgledna; przy wymuszeniu szerokopasmowym D mierzy glownie wymuszenie.
"""
from __future__ import annotations

from typing import Dict, Optional

import numpy as np

REGIME_LO, REGIME_HI = 0.3, 3.0


def n_cycles(window_s: float, f_rhythm: float) -> float:
    return float(window_s * f_rhythm)


def band_envelope(x, fs, lo, hi):
    x = np.asarray(x, float) - np.mean(x); X = np.fft.fft(x); f = np.fft.fftfreq(len(x), 1 / fs)
    Z = np.zeros_like(X); m = (f >= lo) & (f < hi); Z[m] = 2 * X[m]
    return np.abs(np.fft.ifft(Z))


def event_density(env, fs, k=5.0):
    """Gestosc zdarzen D bez progu: wypelnienie obwiedni eta, D = eta / (1 - eta). Pomocniczo: czestosc zdarzen r
    (maksima > mediana + k*MAD, odstep >= 3 tau) i tau (autokorelacja obwiedni < 1/e)."""
    e = np.asarray(env, float)
    eta = float(e.mean() ** 2 / (np.mean(e ** 2) + 1e-30))
    a = e - e.mean()
    ac = np.fft.irfft(np.abs(np.fft.rfft(a, 2 * len(a))) ** 2)[: len(a)]; ac = ac / (ac[0] + 1e-30)
    lag = int(np.argmax(ac < np.exp(-1))) if np.any(ac < np.exp(-1)) else len(a)
    med = np.median(e); mad = 1.4826 * np.median(np.abs(e - med)) + 1e-30
    pk = np.where((e[1:-1] > e[:-2]) & (e[1:-1] >= e[2:]) & (e[1:-1] > med + k * mad))[0] + 1
    ev, last = 0, -np.inf
    for p in pk:
        if p - last >= 3 * max(lag, 1):
            ev += 1; last = p
    return {"D": eta / max(1 - eta, 1e-9), "eta": eta, "rate": float(ev / (len(e) / fs)), "tau": float(max(lag, 1) / fs)}


def regime(D: float) -> str:
    return "czasteczka" if D < REGIME_LO else ("fala" if D > REGIME_HI else "pakiet")


def feasibility(N_cyk: float, L_koh: float, D: float, anchor: str) -> dict:
    """Regula wykonalnosci: ktora droga i czy sito ma szanse -- liczona PRZED testem."""
    path, ok = [], True
    if N_cyk < 10:
        path.append("za malo cykli w oknie (N_cyk < 10): grzebien rozmyty"); ok = False
    if np.isfinite(L_koh) and L_koh < N_cyk:
        path.append("koherencja krotsza niz okno: wyprostowac rure (zegar katowy/zdarzeniowy)")
    if anchor == "wolna":
        path.append("brak kotwicy: samokorekta bez punktu startu"); ok = False
    reg = regime(D)
    path.append({"czasteczka": "miara czasteczkowosci P (blyski)", "pakiet": "sito z kotwica (grzebien Q)",
                 "fala": "linie galezi K (harmoniczne kotwicy)"}[reg])
    return {"reżim": reg, "droga": path, "sito_ma_szanse": ok}


def measure(x, fs: float, lo: float, hi: float, k: float = 5.0) -> Dict[str, object]:
    """tau, rho (= D) i rezim sygnalu x w pasmie [lo, hi). Zwraca tez eta i czestosc zdarzen."""
    ed = event_density(band_envelope(x, fs, lo, min(hi, fs / 2)), fs, k)
    return {"tau": ed["tau"], "rho": ed["D"], "eta": ed["eta"], "rate": ed["rate"], "rezim": regime(ed["D"])}


def relative_to_background(rho: float, rho_background: float) -> float:
    """rho wzgledem tla tej samej maszyny/konstrukcji (np. poczatek zycia, stan wzorcowy). < 1: ku czasteczce."""
    return float(rho / max(rho_background, 1e-12))


def measured_state(x, fs: float, lo: float, hi: float, Lambda: float = 0.0, J: float = 0.0,
                   rho_background: Optional[float] = None):
    """MetaState z mierzonymi tau i rho (rho wzgledem tla, gdy podane). Lambda i J pozostaja z modelu uzytkownika."""
    from core_meta.meta_state import MetaState
    m = measure(x, fs, lo, hi)
    rho = m["rho"] if rho_background is None else relative_to_background(m["rho"], rho_background)
    return MetaState(Lambda=Lambda, tau=m["tau"], rho=rho, J=J)
