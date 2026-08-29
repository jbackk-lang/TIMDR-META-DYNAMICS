"""test_trefoil_torsion_vs_tau.py

Test-dygresja od SKILL.14.2 (helisa: torsion vs tau, wynik ujemny). Uzytkownik
postawil hipoteze: skoro (a) helisa ma prawie stala torsje, i (b) uzyta seria
demo NIE byla czysta helisa - to moze prawdziwa "helisa-jak-w-glowie" to
wezel trojlistny (zamkniety splot toroidalny, torsja NIEstala - potwierdzone
osobno analitycznie sympy: zakres ok. -0.22..0.35, std 0.18), i na TAKIEJ
krzywej geometryczna torsja MOZE korelowac z osia nazwana "tau".

PRE-REJESTRACJA (przed uruchomieniem, protokol SKILL SS13):
- Obiekt: standardowa parametryzacja wezla trojlistnego,
    x(t) = sin(t) + 2*sin(2t)
    y(t) = cos(t) - 2*cos(2t)
    z(t) = -sin(3t)
  probkowana rownomiernie w t na [0, 2*pi) w n=60 punktach (ta sama liczba
  punktow co seria demo MetaState, dla porownywalnosci).
- Mapowanie (Lambda, tau, rho) = (x, y, z) - DOKLADNIE ta sama konwencja
  kolejnosci co w field_torsion()/MetaState (Lambda,tau,rho), tau = y(t).
  To jest arbitralny wybor ktorej wspolrzednej nazwac "tau" (krzywa nie ma
  wyroznionej osi) - jawnie przyznany, nie ukrywany.
- Wielkosci: torsion = field_torsion(states, dt=2*pi/60)[1] (dokladnie ta
  sama, juz zweryfikowana funkcja co w tescie helisy/demo), tau = [s.tau
  for s in states] = y(t_i).
- Metryka: Spearman, ten sam indeks, bez przesuniec.
- Model null: permutacja N=10000, tasowanie tau, p dwustronne.
- Uruchomienie: RAZ.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import spearmanr

from core_meta.meta_state import MetaState
from analysis.meta_torsion import field_torsion


def build_trefoil_states(n: int = 60):
    ts = np.linspace(0, 2 * np.pi, n, endpoint=False)
    x = np.sin(ts) + 2 * np.sin(2 * ts)
    y = np.cos(ts) - 2 * np.cos(2 * ts)
    z = -np.sin(3 * ts)
    states = [MetaState(Lambda=xi, tau=yi, rho=zi, J=0.0) for xi, yi, zi in zip(x, y, z)]
    dt = ts[1] - ts[0]
    return states, dt


def main():
    states, dt = build_trefoil_states(n=60)
    kappa, torsion = field_torsion(states, dt=dt)
    tau = np.array([s.tau for s in states])

    print(f"n={len(states)}, dt={dt:.5f}")
    print(f"torsion: min={torsion.min():.4f} max={torsion.max():.4f} std={torsion.std():.4f}")
    print(f"tau:     min={tau.min():.4f} max={tau.max():.4f} std={tau.std():.4f}")

    rho_obs, p_asymp = spearmanr(torsion, tau)
    print(f"\nSpearman rho (torsion vs tau) = {rho_obs:.4f} (p asymptotyczne = {p_asymp:.4g})")

    rng = np.random.default_rng(0)
    n_perm = 10000
    perm_rhos = np.empty(n_perm)
    tau_shuffled = tau.copy()
    for i in range(n_perm):
        rng.shuffle(tau_shuffled)
        perm_rhos[i] = spearmanr(torsion, tau_shuffled)[0]

    p_perm = np.mean(np.abs(perm_rhos) >= abs(rho_obs))
    print(f"Test permutacyjny (N={n_perm}): p = {p_perm:.4f}")
    print(f"Rozklad null: mean={perm_rhos.mean():.4f} std={perm_rhos.std():.4f}")

    print("\n--- WERDYKT ---")
    if p_perm < 0.05:
        print(f"Istotna korelacja monotoniczna (p={p_perm:.4f} < 0.05), rho={rho_obs:.4f}.")
    else:
        print(f"BRAK istotnej korelacji monotonicznej (p={p_perm:.4f} >= 0.05).")


if __name__ == "__main__":
    main()
