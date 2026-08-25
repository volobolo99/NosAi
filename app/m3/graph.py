from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(frozen=True)
class CausalEdge:
    source: str
    target: str
    weight: float = 1.0

@dataclass
class CausalGraph:
    nodes: set[str] = field(default_factory=set)
    edges: list[CausalEdge] = field(default_factory=list)

    def add_node(self, node: str) -> None:
        self.nodes.add(node)

    def add_edge(self, source: str, target: str, weight: float = 1.0) -> None:
        if source == target:
            raise ValueError("self-causal edges are not allowed")
        self.nodes.update((source, target))
        self.edges.append(CausalEdge(source, target, float(weight)))
        if self.has_cycle():
            self.edges.pop()
            raise ValueError("causal graph must remain acyclic")

    def parents(self, node: str) -> list[CausalEdge]:
        return [e for e in self.edges if e.target == node]

    def children(self, node: str) -> list[CausalEdge]:
        return [e for e in self.edges if e.source == node]

    def topological_order(self) -> list[str]:
        indegree = {n: 0 for n in self.nodes}
        for e in self.edges:
            indegree[e.target] += 1
        queue = [n for n, d in indegree.items() if d == 0]
        order: list[str] = []
        while queue:
            n = queue.pop(0)
            order.append(n)
            for e in self.children(n):
                indegree[e.target] -= 1
                if indegree[e.target] == 0:
                    queue.append(e.target)
        if len(order) != len(self.nodes):
            raise ValueError("causal graph contains a cycle")
        return order

    def has_cycle(self) -> bool:
        try:
            self.topological_order()
            return False
        except ValueError:
            return True
