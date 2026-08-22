class MetaPredict:
    """
    Predykcja przyszłego stanu pola TIMDR.
    """

    def predict_next(self, current_state, M_state, dt):
        return MetaState(
            Lambda=current_state.Lambda + M_state.Lambda * dt,
            tau=current_state.tau + M_state.tau * dt,
            rho=current_state.rho + M_state.rho * dt,
            J=current_state.J + M_state.J * dt
        )
