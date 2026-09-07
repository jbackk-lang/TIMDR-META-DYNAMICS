"""analysis/meta_torsion.py

field_curvature() i field_torsion(): PRAWDZIWA krzywizna i torsja
(standardowe wzory Freneta-Serreta) trajektorii pola meta w przestrzeni
(Λ, τ, ρ) - dokładnie tej samej trajektorii, którą rysuje
visualization/meta_flow_3d.py.

DLACZEGO OSOBNY PLIK, A NIE ZMIANA MetaState.tau:
MetaState.tau ("transformacja", core_meta/meta_state.py) to skalar
WEJŚCIOWY - nie ma żadnego zdefiniowanego wzoru, po prostu wpisywana
liczba. models/evolution_helix.py klasyfikuje na nim narodziny/
stabilizację/rozpad progami 0.2/1.0, i sam jawnie przyznaje w swoim
docstringu, że to "arbitralne wartości ze szkicu, do skalibrowania".
To zupełnie inny byt niż torsja (skręcenie) krzywej z geometrii
różniczkowej. Ten sam symbol (τ) nie oznacza tej samej wielkości -
dokładnie tę pomyłkę (etykieta ≠ definicja) trzeba było w tej samej
sesji kilka razy oddzielać przy okazji niezwiązanej hipotezy
geometrycznej użytkownika. Żeby jej tu nie powielić, wynik tego modułu
to NOWE pole (field_curvature/field_torsion), nie nadpisanie τ.

CO TU JEST LICZONE:
S_meta(t) = (Λ(t), τ(t), ρ(t)) to krzywa w R^3. Jej krzywizna i torsja:

    kappa   = |r' x r''| / |r'|^3
    torsion = ((r' x r'') . r''') / |r' x r''|^2

gdzie r', r'', r''' to pierwsza/druga/trzecia pochodna pozycji po
parametrze (tu: krok * dt). Ta sama matematyka i te same wzory co
FLIGHT-TRACKING-TIMDR.frenet_serret() (zweryfikowane tam numerycznie na
helisie kołowej, błąd względny < 1e-5) - przepisane tutaj samodzielnie
(bez zależności międzyrepo) i dostosowane do zwykle znacznie krótszych
serii stanu meta (rzędu dziesiątek punktów, nie tysięcy próbek ADS-B).

OGRANICZENIE (to samo co we FLIGHT-TRACKING-TIMDR, z tego samego powodu):
torsion wymaga TRZECIEJ pochodnej - surowe różnicowanie wzmacnia szum.
Dlatego pozycja jest najpierw wygładzana filtrem Savitzky-Golay (jeśli
scipy jest dostępne), a różniczkowana analitycznie z dopasowanego
wielomianu, nie punkt-po-punkcie. Krótkie serie (< poly+3 punktów)
zwracają same zera zamiast rzucać wyjątek w środku pipeline'u.

CZY field_torsion KORELUJE Z τ (input)? Nieznane - nikt tego jeszcze nie
zmierzył na realnych danych tego repo. Byłby to ciekawy, sprawdzalny
wynik, ale to wymaga faktycznego pomiaru, nie założenia.
"""
from __future__ import annotations

from typing import List, Tuple

import numpy as np

from core_meta.meta_state import MetaState

try:
    from scipy.signal import savgol_filter
    _HAS_SCIPY = True
except ImportError:  # pragma: no cover - zalezy od srodowiska
    _HAS_SCIPY = False


def field_torsion(
    states: List[MetaState],
    dt: float = 1.0,
    poly: int = 3,
) -> Tuple[np.ndarray, np.ndarray]:
    """Liczy (field_curvature, field_torsion) trajektorii (Λ, τ, ρ).

    `dt`: krok między kolejnymi stanami, zakładany STAŁY - jeśli stany nie
    są równoodległe, wynik będzie błędny (tak jak przy każdej metodzie
    różnicowej na nierównym kroku - to samo założenie co w
    MetaPredict.simulate_future()).

    Zwraca (kappa, torsion), oba tablice numpy długości len(states).
    """
    n = len(states)
    n_needed = poly + 3
    if n < n_needed:
        z = np.zeros(n)
        return z, z.copy()

    pos = np.array([[s.Lambda, s.tau, s.rho] for s in states], dtype=float)

    if _HAS_SCIPY:
        max_win = n if n % 2 == 1 else n - 1
        win = min(9, max_win)
        if win <= poly:
            win = poly + 2 if (poly + 2) % 2 == 1 else poly + 3
            win = min(win, max_win)
        if win <= poly:
            z = np.zeros(n)
            return z, z.copy()

        v = savgol_filter(pos, window_length=win, polyorder=poly, deriv=1, delta=dt, axis=0)
        a = savgol_filter(pos, window_length=win, polyorder=poly, deriv=2, delta=dt, axis=0)
        j = savgol_filter(pos, window_length=win, polyorder=poly, deriv=3, delta=dt, axis=0)
    else:  # pragma: no cover - brak scipy: rozniczkowanie skonczone, gorsza jakosc
        v = np.gradient(pos, dt, axis=0)
        a = np.gradient(v, dt, axis=0)
        j = np.gradient(a, dt, axis=0)

    cross_va = np.cross(v, a)
    speed = np.linalg.norm(v, axis=1)
    cross_norm = np.linalg.norm(cross_va, axis=1)

    kappa = np.zeros(n)
    torsion = np.zeros(n)
    ok_speed = speed > 1e-9
    kappa[ok_speed] = cross_norm[ok_speed] / (speed[ok_speed] ** 3)
    ok_cross = cross_norm > 1e-9
    numer = np.einsum('ij,ij->i', cross_va, j)
    torsion[ok_cross] = numer[ok_cross] / (cross_norm[ok_cross] ** 2)
    return kappa, torsion
