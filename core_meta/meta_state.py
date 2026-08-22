class MetaState:
    """
    Reprezentacja globalnego stanu pola TIMDR:
    Λ – struktura
    τ – transformacja
    ρ – anomalia
    J – operator punktowy
    """

    def __init__(self, Lambda, tau, rho, J):
        self.Lambda = Lambda
        self.tau = tau
        self.rho = rho
        self.J = J

    def delta(self, other):
        """
        Różnica między dwoma stanami pola.
        """
        return MetaState(
            Lambda=other.Lambda - self.Lambda,
            tau=other.tau - self.tau,
            rho=other.rho - self.rho,
            J=other.J - self.J
        )
