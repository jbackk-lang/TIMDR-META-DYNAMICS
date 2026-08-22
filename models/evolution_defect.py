class DefectEvolution:
    """
    Ewolucja defektów/anomalii w polu TIMDR.
    """

    def track(self, defect_states):
        phases = []

        for state in defect_states:
            if state.rho < 0.3:
                phases.append("lokalna anomalia")
            elif state.rho < 1.0:
                phases.append("rozszerzająca się anomalia")
            else:
                phases.append("globalny defekt")

        return phases
