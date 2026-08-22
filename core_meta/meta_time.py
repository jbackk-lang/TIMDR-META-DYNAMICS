class MetaTime:
    """
    Meta‑czas: miara zmiany struktury pola TIMDR.
    """

    def compute(self, delta_state):
        """
        T_meta = f(ΔΛ, Δτ, Δρ, ΔJ)
        """
        return (
            abs(delta_state.Lambda)
            + abs(delta_state.tau)
            + abs(delta_state.rho)
            + abs(delta_state.J)
        )

    def normalize(self, value):
        """
        Normalizacja meta‑czasu do zakresu 0–1.
        """
        return value / (1 + value)
