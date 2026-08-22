# timdr_meta_dynamics/__init__.py

from dataclasses import dataclass
from typing import List


# =========================
# CORE: STAN POLA I META-CZAS
# =========================

@dataclass
class MetaState:
    """
    Globalny stan pola TIMDR:
    Λ – struktura
    τ – transformacja
    ρ – anomalia
    J – operator punktowy
    """
    Lambda: float
    tau: float
    rho: float
    J: float

    def delta(self, other: "MetaState") -> "MetaState":
        return MetaState(
            Lambda=other.Lambda - self.Lambda,
            tau=other.tau - self.tau,
            rho=other.rho - self.rho,
            J=other.J - self.J,
        )


class MetaTime:
    """
    Meta‑czas: miara zmiany struktury pola TIMDR.
    """

    def compute(self, delta_state: MetaState) -> float:
        return (
            abs(delta_state.Lambda)
            + abs(delta_state.tau)
            + abs(delta_state.rho)
            + abs(delta_state.J)
        )

    def normalize(self, value: float) -> float:
        return value / (1.0 + value)


# =========================
# CORE: OPERATOR M
# =========================

class MetaOperatorM:
    """
    Operator ewolucji pola:
    M = d/dt (Λ, τ, ρ, J)
    """

    def compute(self, prev_state: MetaState, next_state: MetaState, dt: float) -> MetaState:
        if dt == 0:
            raise ValueError("dt must be non-zero")

        delta = prev_state.delta(next_state)

        return MetaState(
            Lambda=delta.Lambda / dt,
            tau=delta.tau / dt,
            rho=delta.rho / dt,
            J=delta.J / dt,
        )

    def magnitude(self, M_state: MetaState) -> float:
        return (
            abs(M_state.Lambda)
            + abs(M_state.tau)
            + abs(M_state.rho)
            + abs(M_state.J)
        )

    def classify_phase(self, M_state: MetaState) -> str:
        mag = self.magnitude(M_state)

        if mag < 0.1:
            return "stabilna"
        elif mag < 1.0:
            return "przejściowa"
        else:
            return "krytyczna"


# =========================
# MODELE EWOLUCJI
# =========================

class FieldEvolution:
    """
    Ewolucja globalnego pola TIMDR.
    """

    def __init__(self, meta_operator: MetaOperatorM):
        self.meta_operator = meta_operator

    def simulate(self, states: List[MetaState], dt: float) -> List[MetaState]:
        M_series: List[MetaState] = []

        for i in range(len(states) - 1):
            M = self.meta_operator.compute(states[i], states[i + 1], dt)
            M_series.append(M)

        return M_series


class HelixEvolution:
    """
    Ewolucja helis: narodziny, stabilizacja, rozpad.
    """

    def track(self, helix_states: List[MetaState]) -> List[str]:
        lifecycle: List[str] = []

        for state in helix_states:
            if state.tau < 0.2:
                lifecycle.append("narodziny")
            elif state.tau < 1.0:
                lifecycle.append("stabilizacja")
            else:
                lifecycle.append("rozpad")

        return lifecycle


class DefectEvolution:
    """
    Ewolucja defektów/anomalii w polu TIMDR.
    """

    def track(self, defect_states: List[MetaState]) -> List[str]:
        phases: List[str] = []

        for state in defect_states:
            if state.rho < 0.3:
                phases.append("lokalna anomalia")
            elif state.rho < 1.0:
                phases.append("rozszerzająca się anomalia")
            else:
                phases.append("globalny defekt")

        return phases


# =========================
# ANALIZA: MAPA I PREDYKCJA
# =========================

class MetaMap:
    """
    Mapa zmian pola w czasie.
    """

    def __init__(self, meta_operator: MetaOperatorM):
        self.meta_operator = meta_operator

    def build(self, states: List[MetaState], M_series: List[MetaState]) -> dict:
        return {
            "states": states,
            "meta_operator": M_series,
        }

    def detect_transitions(self, M_series: List[MetaState]) -> List[str]:
        transitions: List[str] = []

        for M in M_series:
            phase = self.meta_operator.classify_phase(M)
            transitions.append(phase)

        return transitions


class MetaPredict:
    """
    Predykcja przyszłego stanu pola TIMDR.
    """

    def predict_next(self, current_state: MetaState, M_state: MetaState, dt: float) -> MetaState:
        return MetaState(
            Lambda=current_state.Lambda + M_state.Lambda * dt,
            tau=current_state.tau + M_state.tau * dt,
            rho=current_state.rho + M_state.rho * dt,
            J=current_state.J + M_state.J * dt,
        )

    def simulate_future(
        self,
        current_state: MetaState,
        M_series: List[MetaState],
        dt: float,
    ) -> List[MetaState]:
        states: List[MetaState] = [current_state]

        for M in M_series:
            next_state = self.predict_next(states[-1], M, dt)
            states.append(next_state)

        return states


# =========================
# WIZUALIZACJA (MINIMALNA)
# =========================

class MetaPhaseDiagram:
    """
    Diagram faz meta‑pola (wersja tekstowa).
    """

    def plot(self, phases: List[str]) -> None:
        for i, phase in enumerate(phases):
            print(f"{i}: {phase}")
