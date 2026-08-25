"""M1 integration facade for the historical v4.8 learning loop."""
from dataclasses import dataclass
from .adapters import to_m1_state, to_m1_action, SandboxWorldModel
from .core.types import PerformanceMetrics, CurriculumStage, Transition
from .curriculum import CurriculumManager
from .dataset import DataValidator
from .experience import ExperienceQualityScorer
from .ood import OODDetector
from .replay import PrioritizedReplay
from .shift import ShiftDetector
from .world_model import WorldModelEnsemble, LatentWorldModel


@dataclass
class M1StepResult:
    transition: Transition
    quality: object
    shift: object
    ood: object


class M1LearningStack:
    """Coordinates M1 modules without taking ownership of the v4.8 planner."""
    def __init__(self, reference_features, replay_capacity=100000, seed=42, shift_threshold=15.0, ood_threshold=15.0):
        self.validator = DataValidator()
        self.quality = ExperienceQualityScorer()
        self.replay = PrioritizedReplay(replay_capacity, seed=seed)
        self.shift = ShiftDetector(reference_features, threshold=shift_threshold)
        self.ood = OODDetector(reference_features, threshold=ood_threshold)
        self.curriculum = CurriculumManager([
            CurriculumStage("warmup", 0.0, 20, 0.0, 0.1, 0.2, 0.60),
            CurriculumStage("basic", 0.4, 40, 0.2, 0.2, 0.4, 0.70),
            CurriculumStage("advanced", 0.8, 80, 0.5, 0.4, 0.7, 0.80),
        ], seed=seed)
        # Start with independent learnable models. Before training they are uncalibrated;
        # after train_world_model() they provide genuine epistemic disagreement.
        self.latent_world_model = LatentWorldModel(action_dim=3, latent_dim=8, seed=seed)
        # Preserve the historical deterministic sandbox until a learned ensemble
        # has been trained; this keeps legacy callers backward-compatible.
        self.world_model = WorldModelEnsemble([SandboxWorldModel(), SandboxWorldModel(), SandboxWorldModel()])
        self._wm_seed = seed
        self.world_model_trained = False

    def train_world_model(self, transitions, epochs=25, batch_size=32):
        transitions = list(transitions)
        if not transitions:
            raise ValueError("transitions required")
        # Bootstrap each member independently to create genuine model disagreement.
        import random
        models = []
        n = len(transitions)
        for i in range(3):
            rng = random.Random(self._wm_seed + i)
            sample = [transitions[rng.randrange(n)] for _ in range(n)]
            model = LatentWorldModel(action_dim=3, latent_dim=8, seed=self._wm_seed + i)
            result = model.train(sample, epochs=epochs, batch_size=batch_size)
            model.training_result = result
            models.append(model)
        self.world_model = WorldModelEnsemble(models)
        self.world_model_trained = True
        # Keep the first trained model as the latent backend used by M2.
        self.latent_world_model = models[0]
        return {
            "members": len(models),
            "training": [m.training_result for m in models],
        }

    def observe_transition(self, previous, action, next_state, reward, done, info=None):
        t = Transition(
            to_m1_state(previous),
            to_m1_action(action),
            float(reward),
            to_m1_state(next_state),
            bool(done),
            info or {},
        )
        validation = self.validator.validate(t)
        if not validation["valid"]:
            raise ValueError("invalid M1 transition: " + "; ".join(validation["errors"]))
        shift = self.shift.evaluate(t.next_state)
        ood = self.ood.evaluate(t.next_state)
        enriched = Transition(t.state, t.action, t.reward, t.next_state, t.done,
                              {**t.info, "shift": shift.score, "ood": ood.score,
                               "uncertainty": ood.score})
        quality = self.quality.score(enriched)
        self.replay.add(enriched, priority=max(quality.total, 1e-6))
        return M1StepResult(enriched, quality, shift, ood)

    def update_curriculum(self, success_rate, mean_reward, failure_rate=0.0, ood_rate=0.0):
        return self.curriculum.evaluate(PerformanceMetrics(
            success_rate, mean_reward, failure_rate, ood_rate
        ))
