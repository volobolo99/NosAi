from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable
import copy
from .graph import CausalGraph

Equation = Callable[[dict[str, float]], float]

@dataclass(frozen=True)
class Intervention:
    values: dict[str, float]

@dataclass(frozen=True)
class SimulationResult:
    values: dict[str, float]
    intervention: dict[str, float] = field(default_factory=dict)

class CausalSimulator:
    """Small deterministic structural-causal-model engine.

    Each node can have a structural equation. `intervene()` implements do(X=x)
    by replacing the equation for intervened variables while preserving all
    downstream causal mechanisms.
    """
    def __init__(self, graph: CausalGraph, equations: dict[str, Equation] | None = None):
        self.graph = graph
        self.equations = dict(equations or {})

    def set_equation(self, node: str, equation: Equation) -> None:
        self.graph.add_node(node)
        self.equations[node] = equation

    def simulate(self, context: dict[str, float], intervention: Intervention | None = None) -> SimulationResult:
        values = copy.deepcopy({k: float(v) for k, v in context.items()})
        forced = dict(intervention.values) if intervention else {}
        for node in self.graph.topological_order():
            if node in forced:
                values[node] = float(forced[node])
                continue
            equation = self.equations.get(node)
            if equation is not None:
                values[node] = float(equation(values))
            else:
                values.setdefault(node, 0.0)
        return SimulationResult(values, forced)

    def intervene(self, context: dict[str, float], values: dict[str, float]) -> SimulationResult:
        return self.simulate(context, Intervention(values))

    def effect(self, context: dict[str, float], intervention: dict[str, float], outcome: str) -> float:
        baseline = self.simulate(context).values.get(outcome, 0.0)
        treated = self.intervene(context, intervention).values.get(outcome, 0.0)
        return treated - baseline
