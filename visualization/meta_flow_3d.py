"""visualization/meta_flow_3d.py

DODANE OD ZERA: ten plik był wymieniony w README ("meta_flow_3d.py —
wizualizacja przepływu meta") i importowany donikąd - w repo GO NIE
BYŁO (sprawdzone: żądanie raw.githubusercontent.com do tego pliku
zwracało pustą odpowiedź / 404, w przeciwieństwie do reszty plików z
tego samego folderu, które istniały). To jedyny plik w tym pakiecie,
który nie jest naprawą istniejącego kodu, tylko nowym dodatkiem.

plot_meta_flow(S_series) rysuje trajektorię pola w przestrzeni (Λ, τ, ρ)
jako linię 3D, z kolorem punktów skalowanym po J (nie po czasie/indeksie -
J jest osobnym, niezależnym wymiarem stanu, więc niesie dodatkową
informację, której nie widać na samej trajektorii Λ-τ-ρ).

Wymaga matplotlib (patrz requirements.txt). Jeśli matplotlib nie jest
zainstalowany, funkcja rzuca czytelny ImportError zamiast cichego
crasha przy próbie użycia mpl_toolkits.
"""
from __future__ import annotations

from typing import List

from core_meta.meta_state import MetaState


def plot_meta_flow(S_series: List[MetaState], show: bool = True, save_path: str | None = None):
    """Rysuje trajektorię pola (Λ, τ, ρ) w 3D, kolorowaną po J.

    Zwraca (fig, ax) z matplotlib, żeby wywołujący mógł dalej modyfikować
    wykres (dodać tytuł, zapisać w innym formacie, itd.) zamiast być
    ograniczonym do tego, co ta funkcja robi sama.

    `show=False` pozwala wywołać to w testach/CI bez otwierania okna.
    `save_path`, jeśli podany, zapisuje wykres do pliku (np. PNG).
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - zależy od środowiska
        raise ImportError(
            "plot_meta_flow() wymaga matplotlib - zainstaluj: pip install matplotlib"
        ) from exc

    if not S_series:
        raise ValueError("S_series jest puste - nie ma czego rysować")

    xs = [s.Lambda for s in S_series]
    ys = [s.tau for s in S_series]
    zs = [s.rho for s in S_series]
    js = [s.J for s in S_series]

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    ax.plot(xs, ys, zs, color="gray", linewidth=0.8, alpha=0.6)
    scatter = ax.scatter(xs, ys, zs, c=js, cmap="viridis", s=20)
    fig.colorbar(scatter, ax=ax, label="J (operator punktowy)")

    ax.set_xlabel("Λ (struktura)")
    ax.set_ylabel("τ (transformacja)")
    ax.set_zlabel("ρ (anomalia)")
    ax.set_title("Przepływ meta-pola TIMDR")

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()

    return fig, ax
