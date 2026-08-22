"""core_meta/meta_state.py

Definicja stanu pola TIMDR na poziomie meta: S_meta(t) = {Λ, τ, ρ, J}.

NAPRAWIONE: to jest teraz jedyne miejsce, gdzie MetaState jest
zdefiniowany. W oryginalnym repo ta sama klasa była zduplikowana
osobno w timdr_meta_dynamics/__init__.py (jako @dataclass, z innym
poziomem wykończenia niż tutaj) - dwie kopie tej samej rzeczy to
klasyczne źródło rozjazdu (poprawisz jedną, zapomnisz drugą - dokładnie
ten sam problem, jaki był z synoptyk-f.py/synoptyk_f.py w innym Twoim
repo). Teraz timdr_meta_dynamics/__init__.py tylko re-eksportuje stąd,
nie definiuje własnej kopii.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MetaState:
    """Globalny stan pola TIMDR:
    Λ (Lambda) – struktura
    τ (tau)    – transformacja
    ρ (rho)    – anomalia
    J          – operator punktowy
    """

    Lambda: float
    tau: float
    rho: float
    J: float

    def delta(self, other: "MetaState") -> "MetaState":
        """Różnica (other - self), zgodnie z konwencją compute_meta_time(S_prev, S_now)."""
        return MetaState(
            Lambda=other.Lambda - self.Lambda,
            tau=other.tau - self.tau,
            rho=other.rho - self.rho,
            J=other.J - self.J,
        )
