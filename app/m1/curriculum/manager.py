from dataclasses import dataclass
from random import Random
from ..core.types import CurriculumStage, PerformanceMetrics

class CurriculumManager:
    def __init__(self, stages: list[CurriculumStage], seed: int = 0):
        if not stages: raise ValueError("at least one curriculum stage is required")
        self.stages = stages; self.index = 0; self.rng = Random(seed)
    def current_stage(self): return self.stages[self.index]
    def evaluate(self, metrics: PerformanceMetrics):
        threshold = self.current_stage().reward_threshold
        if metrics.success_rate >= threshold and self.index < len(self.stages)-1:
            self.index += 1; return "ADVANCE"
        if metrics.success_rate < threshold * 0.5 and self.index > 0:
            self.index -= 1; return "REGRESS"
        return "HOLD"
    def advance(self):
        if self.index < len(self.stages)-1: self.index += 1
    def regress(self):
        if self.index > 0: self.index -= 1
    def sample_scenario(self):
        s=self.current_stage()
        return {"difficulty":s.difficulty,"horizon":s.horizon,"opponent_strength":s.opponent_strength,"uncertainty":s.uncertainty,"state_complexity":s.state_complexity}
