"""test_field_torsion_vs_tau.py

Domyka pytanie z SKILL §14 pkt 2 (i wcześniej §19 pkt 2): czy geometryczna
torsja trajektorii (Lambda, tau, rho) - field_torsion() z
analysis/meta_torsion.py - koreluje z surowym wejsciowym polem tau
(MetaState.tau, "transformacja", bez zdefiniowanego wzoru)?

PRE-REJESTRACJA (przed uruchomieniem, zgodnie z protokolem SKILL §13):
- Obiekty: states = run_meta_analysis()["states"] - jedyna faktyczna seria
  MetaState produkowana przez ten repo (main.py, uzywana tez w
  tests/test_meta_dynamics.py), NIE nowa seria wymyslona pod ten test.
  Zrodlo: load_demo_series(n=60, seed=42) -> build_meta_states_from_market()
  (sinusoida + szum + jeden wstrzykniety skok w polowie - synteyczne dane
  demo, bo analizator3_core, prawdziwe zrodlo rynkowe, nie istnieje w tym
  sandboxie - potwierdzone grepem, brak takiego modulu gdziekolwiek).
- Wielkosci: torsion = field_torsion(states, dt=1.0)[1] (drugi element
  krotki, patrz docstring), tau = [s.tau for s in states]. Ten sam indeks,
  bez przesuniec fazowych (dokladnie jak w SKILL case study 4).
- Metryka: korelacja Spearmana (monotoniczna, odporna na skale/nieliniowosc).
- Model null: test permutacyjny, N=10000 przetasowan jednej serii,
  p dwustronne = udzial |rho_perm| >= |rho_obserwowane|.
- Uruchomienie: RAZ, bez przeszukiwania wariantow/okien/przesuniec.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import spearmanr

from main import run_meta_analysis
from analysis.meta_torsion import field_torsion


def main():
    result = run_meta_analysis()
    states = result["states"]
    print(f"Liczba stanow (n): {len(states)}")

    kappa, torsion = field_torsion(states, dt=1.0)
    tau = np.array([s.tau for s in states])

    print(f"torsion: min={torsion.min():.4f} max={torsion.max():.4f} "
          f"std={torsion.std():.4f}")
    print(f"tau:     min={tau.min():.4f} max={tau.max():.4f} "
          f"std={tau.std():.4f}")

    rho_obs, p_asymp = spearmanr(torsion, tau)
    print(f"\nSpearman rho (torsion vs tau) = {rho_obs:.4f} "
          f"(p asymptotyczne = {p_asymp:.4g})")

    rng = np.random.default_rng(0)
    n_perm = 10000
    perm_rhos = np.empty(n_perm)
    tau_shuffled = tau.copy()
    for i in range(n_perm):
        rng.shuffle(tau_shuffled)
        perm_rhos[i] = spearmanr(torsion, tau_shuffled)[0]

    p_perm = np.mean(np.abs(perm_rhos) >= abs(rho_obs))
    print(f"Test permutacyjny (N={n_perm}): p = {p_perm:.4f}")
    print(f"Rozklad null: mean={perm_rhos.mean():.4f} "
          f"std={perm_rhos.std():.4f}")

    # Bonus (nie byl w pre-rejestracji, ale za darmo z tego samego wywolania
    # field_torsion): to samo dla krzywizny kappa, zeby nie trzeba bylo
    # osobno pytac pozniej.
    rho_kappa, p_kappa_asymp = spearmanr(kappa, tau)
    perm_rhos_k = np.empty(n_perm)
    tau_shuffled2 = tau.copy()
    for i in range(n_perm):
        rng.shuffle(tau_shuffled2)
        perm_rhos_k[i] = spearmanr(kappa, tau_shuffled2)[0]
    p_perm_k = np.mean(np.abs(perm_rhos_k) >= abs(rho_kappa))
    print(f"\n[BONUS] Spearman rho (kappa vs tau) = {rho_kappa:.4f}, "
          f"perm p = {p_perm_k:.4f}")

    print("\n--- WERDYKT ---")
    if p_perm < 0.05:
        print(f"Istotna korelacja monotoniczna (p={p_perm:.4f} < 0.05), "
              f"rho={rho_obs:.4f}.")
    else:
        print(f"BRAK istotnej korelacji monotonicznej (p={p_perm:.4f} >= 0.05).")


if __name__ == "__main__":
    main()
