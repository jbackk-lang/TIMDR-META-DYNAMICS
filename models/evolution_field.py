class FieldEvolution:
    """
    Ewolucja globalnego pola TIMDR.
    """

    def simulate(self, states, meta_operator, dt):
        M_series = []

        for i in range(len(states) - 1):
            M = meta_operator.compute(states[i], states[i+1], dt)
            M_series.append(M)

        return M_series
