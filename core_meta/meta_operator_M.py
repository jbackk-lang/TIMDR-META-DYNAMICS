class MetaOperatorM:
    """
    Operator ewolucji pola:
    M = d/dt (Λ, τ, ρ, J)
    """

    def compute(self, prev_state, next_state, dt):
        delta = prev_state.delta(next_state)

        return MetaState(
            Lambda=delta.Lambda / dt,
            tau=delta.tau / dt,
            rho=delta.rho / dt,
            J=delta.J / dt
        )

    def classify_phase(self, M_state):
        """
        Klasyfikacja faz pola:
        - stabilna
        - przejściowa
        - krytyczna
        """
        magnitude = (
            abs(M_state.Lambda)
            + abs(M_state.tau)
            + abs(M_state.rho)
            + abs(M_state.J)
        )

        if magnitude < 0.1:
            return "stabilna"
        elif magnitude < 1.0:
            return "przejściowa"
        else:
            return "krytyczna"
