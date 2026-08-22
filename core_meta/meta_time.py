"""core_meta/meta_time.py

Meta-czas: nie oś czasu, tylko miara zmiany struktury pola między
dwoma stanami. T_meta = g(ΔΛ, Δτ, Δρ, ΔJ).

Ten plik nie zależy od innych modułów (przyjmuje gotowy MetaState.delta()
jako argument), więc zostaje bez zmian względem oryginału - był już
poprawny sam w sobie.
"""
from __future__ import annotations

from core_meta.meta_state import MetaState


class MetaTime:
    """Meta-czas: miara zmiany struktury pola TIMDR."""

    def compute(self, delta_state: MetaState) -> float:
        """T_meta = |ΔΛ| + |Δτ| + |Δρ| + |ΔJ|."""
        return (
            abs(delta_state.Lambda)
            + abs(delta_state.tau)
            + abs(delta_state.rho)
            + abs(delta_state.J)
        )

    def normalize(self, value: float) -> float:
        """Normalizacja meta-czasu do zakresu [0, 1): value / (1 + value)."""
        return value / (1.0 + value)
