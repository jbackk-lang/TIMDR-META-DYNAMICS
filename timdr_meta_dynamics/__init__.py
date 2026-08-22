"""timdr_meta_dynamics/__init__.py

Publiczne API pakietu - to jest jedyne miejsce, z którego main.py (i
każdy inny kod) powinien importować:

    from timdr_meta_dynamics import MetaState, MetaOperatorM, FieldEvolution, ...

NAPRAWIONE: w oryginalnym repo ten plik definiował WŁASNĄ, kompletną
kopię wszystkich klas (MetaState, MetaTime, MetaOperatorM,
FieldEvolution, HelixEvolution, DefectEvolution, MetaMap, MetaPredict,
MetaPhaseDiagram) - równolegle do osobnych plików w core_meta/,
models/, analysis/, visualization/, które README opisuje jako
strukturę repo. Dwie kopie tej samej logiki, rozjeżdżające się cicho
(np. ta wersja miała simulate_future(), którą analysis/meta_predict.py
w ogóle nie miał). Teraz jest jedno źródło prawdy: pliki pod
core_meta/models/analysis/visualization, a ten plik tylko je
re-eksportuje pod płaskim importem, jakiego oczekuje main.py.
"""
from __future__ import annotations

from core_meta.meta_state import MetaState
from core_meta.meta_time import MetaTime
from core_meta.meta_operator_M import MetaOperatorM

from models.evolution_field import FieldEvolution
from models.evolution_helix import HelixEvolution
from models.evolution_defect import DefectEvolution

from analysis.meta_map import MetaMap
from analysis.meta_predict import MetaPredict

from visualization.meta_phase_diagram import MetaPhaseDiagram

__all__ = [
    "MetaState",
    "MetaTime",
    "MetaOperatorM",
    "FieldEvolution",
    "HelixEvolution",
    "DefectEvolution",
    "MetaMap",
    "MetaPredict",
    "MetaPhaseDiagram",
]
