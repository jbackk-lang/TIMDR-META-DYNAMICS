# main.py

from timdr_meta_dynamics import (
    MetaState,
    MetaOperatorM,
    FieldEvolution,
    MetaMap,
    MetaPredict,
)
from analizator3_core import load_market_series  # zakładam, że masz taką funkcję


def build_meta_states_from_market(series):
    """
    Konwersja danych giełdowych na MetaState.
    Tu możesz użyć swojego TRM / flow / twist itd.
    Na razie prosty szkic.
    """
    meta_states = []

    for point in series:
        price = point["price"]
        volume = point["volume"]
        trm = point["trm"]      # np. Twój wskaźnik TIMDR
        flow = point["flow"]    # przepływ informacji

        state = MetaState(
            Lambda=price,
            tau=trm,
            rho=flow,
            J=volume,
        )
        meta_states.append(state)

    return meta_states


def run_meta_analysis():
    # 1. Wczytanie danych z Analizatora Giełdowego 3.0
    market_series = load_market_series("data/market_series.csv")

    # 2. Konwersja na MetaState
    states = build_meta_states_from_market(market_series)

    # 3. Obliczenie M-serii
    meta_operator = MetaOperatorM()
    field_evolution = FieldEvolution(meta_operator)
    dt = 1.0  # krok czasowy – np. 1 jednostka indeksu

    M_series = field_evolution.simulate(states, dt)

    # 4. Mapa i fazy
    meta_map = MetaMap(meta_operator)
    map_data = meta_map.build(states, M_series)
    phases = meta_map.detect_transitions(M_series)

    # 5. Predykcja
    predictor = MetaPredict()
    future_states = predictor.simulate_future(states[-1], M_series[-10:], dt)

    return {
        "states": states,
        "M_series": M_series,
        "phases": phases,
        "future_states": future_states,
        "map_data": map_data,
    }


if __name__ == "__main__":
    result = run_meta_analysis()
    print("Fazy meta-pola:", result["phases"][-20:])
