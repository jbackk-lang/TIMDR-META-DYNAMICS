class HelixEvolution:
    """
    Ewolucja helis: narodziny, stabilizacja, rozpad.
    """

    def track(self, helix_states):
        lifecycle = []

        for state in helix_states:
            if state.tau < 0.2:
                lifecycle.append("narodziny")
            elif state.tau < 1.0:
                lifecycle.append("stabilizacja")
            else:
                lifecycle.append("rozpad")

        return lifecycle
