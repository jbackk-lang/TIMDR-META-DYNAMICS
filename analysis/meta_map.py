class MetaMap:
    """
    Mapa zmian pola w czasie.
    """

    def build(self, states, M_series):
        return {
            "states": states,
            "meta_operator": M_series
        }

    def detect_transitions(self, M_series):
        transitions = []

        for M in M_series:
            phase = MetaOperatorM().classify_phase(M)
            transitions.append(phase)

        return transitions
