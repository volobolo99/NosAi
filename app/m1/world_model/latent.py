"""Learnable latent world model used by M1 and prepared for M2 imagination."""

from __future__ import annotations

from typing import Iterable, Sequence

from app.hardware_profile import detect_hardware
from ..core.types import LatentState, Prediction, State, Action, Uncertainty

try:
    import torch
    from torch import nn
except ImportError:  # pragma: no cover
    torch = None
    nn = None


if nn is not None:

    class _DynamicsNet(nn.Module):
        """Learnable latent dynamics network."""

        def __init__(
            self, state_dim: int, action_dim: int, latent_dim: int, hidden: int = 64
        ) -> None:
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(latent_dim + action_dim, hidden),
                nn.Tanh(),
                nn.Linear(hidden, hidden),
                nn.Tanh(),
            )
            self.next_latent = nn.Linear(hidden, latent_dim)
            self.reward = nn.Linear(hidden, 1)
            self.done = nn.Linear(hidden, 1)
            self.state_head = nn.Linear(latent_dim, state_dim)

        def forward(self, z: torch.Tensor, a: torch.Tensor) -> tuple:
            """Predict next latent, reward, done, and reconstructed state."""
            h = self.net(torch.cat([z, a], dim=-1))
            return (
                self.next_latent(h),
                self.reward(h).squeeze(-1),
                self.done(h).squeeze(-1),
                self.state_head(self.next_latent(h)),
            )

else:

    class _DynamicsNet:  # pragma: no cover - exercised through dependency error
        """Import-safe placeholder when PyTorch is unavailable."""

        def __init__(self, *args, **kwargs) -> None:
            raise RuntimeError("PyTorch is required for the learnable LatentWorldModel")


class LatentWorldModel:
    """Small PyTorch latent dynamics model."""

    def __init__(
        self,
        state_dim: int | None = None,
        action_dim: int = 3,
        latent_dim: int = 8,
        hidden: int = 64,
        seed: int = 42,
        lr: float = 1e-3,
        device: str | None = None,
        train_device: str | None = None,
        gpu_min_samples: int | None = None,
    ) -> None:
        """Initialize latent world model."""
        if torch is None or nn is None:
            raise RuntimeError("PyTorch is required for the learnable LatentWorldModel")
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.latent_dim = latent_dim
        self.hidden = hidden
        self.seed = seed
        self.lr = lr
        profile = detect_hardware()
        requested = device or profile.online_device
        if requested == "auto":
            requested = profile.online_device
        self.device = torch.device(requested)
        if self.device.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA device requested but CUDA is unavailable")
        requested_train = train_device or profile.training_device
        if requested_train == "auto":
            requested_train = profile.training_device
        self.training_device = torch.device(requested_train)
        if self.training_device.type == "cuda" and not torch.cuda.is_available():
            self.training_device = torch.device("cpu")
        self.gpu_min_samples = (
            profile.gpu_training_min_samples
            if gpu_min_samples is None
            else max(1, int(gpu_min_samples))
        )
        self._net = None
        self._optimizer = None

    def _ensure(self, state_dim: int) -> None:
        """Ensure network is initialized."""
        if self._net is not None:
            return
        torch.manual_seed(self.seed)
        self.state_dim = state_dim
        self._encoder = nn.Sequential(
            nn.Linear(state_dim, self.hidden),
            nn.Tanh(),
            nn.Linear(self.hidden, self.latent_dim),
        )
        self._net = _DynamicsNet(state_dim, self.action_dim, self.latent_dim, self.hidden)
        self._decoder = nn.Linear(self.latent_dim, state_dim)
        self._encoder.to(self.device)
        self._net.to(self.device)
        self._decoder.to(self.device)
        self._optimizer = torch.optim.Adam(
            list(self._encoder.parameters())
            + list(self._net.parameters())
            + list(self._decoder.parameters()),
            lr=self.lr,
        )

    @staticmethod
    def _state_vec(state: State) -> list[float]:
        return [float(x) for x in state.features]

    def _action_vec(self, action: Action) -> list[float]:
        p = action.parameters
        vals = [
            (sum(map(ord, action.id)) % 997) / 997.0,
            float(p.get("delta", 0.0)),
            float(p.get("reward", 0.0)),
        ]
        if self.action_dim > 3:
            vals += [0.0] * (self.action_dim - 3)
        return vals[: self.action_dim]

    def encode(self, state: State) -> LatentState:
        self._ensure(len(self._state_vec(state)))
        with torch.no_grad():
            z = self._encoder(torch.tensor([self._state_vec(state)], dtype=torch.float32, device=self.device))[0]
        return LatentState(tuple(float(x) for x in z.tolist()))

    def predict_latent(self, latent: LatentState, action: Action) -> LatentState:
        self._ensure(self.state_dim or len(latent.vector))
        with torch.no_grad():
            z = torch.tensor([latent.vector], dtype=torch.float32, device=self.device)
            a = torch.tensor([self._action_vec(action)], dtype=torch.float32, device=self.device)
            nz, _, _, _ = self._net(z, a)
        return LatentState(tuple(float(x) for x in nz[0].tolist()))

    def predict_reward(self, latent: LatentState, action: Action) -> float:
        self._ensure(self.state_dim or len(latent.vector))
        with torch.no_grad():
            z = torch.tensor([latent.vector], dtype=torch.float32, device=self.device)
            a = torch.tensor([self._action_vec(action)], dtype=torch.float32, device=self.device)
            _, reward, _, _ = self._net(z, a)
        return float(reward.item())

    def predict(self, state: State, action: Action) -> Prediction:
        self._ensure(len(self._state_vec(state)))
        with torch.no_grad():
            x = torch.tensor([self._state_vec(state)], dtype=torch.float32, device=self.device)
            z = self._encoder(x)
            a = torch.tensor([self._action_vec(action)], dtype=torch.float32, device=self.device)
            _, reward, done, next_state_vec = self._net(z, a)
        next_state = State(
            tuple(float(v) for v in next_state_vec[0].tolist()),
            state.timestamp + 1,
            state.scenario_id,
            state.metadata,
        )
        reward_value = float(reward.item())
        return Prediction(next_state, reward_value, float(torch.sigmoid(done).item()), reward_value)

    def rollout_latent(self, latent: LatentState, actions: Sequence[Action]) -> list[LatentState]:
        out = []
        current = latent
        for action in actions:
            current = self.predict_latent(current, action)
            out.append(current)
        return out

    def rollout(self, state: State, actions: Sequence[Action]) -> list[Prediction]:
        out = []
        current = state
        for action in actions:
            prediction = self.predict(current, action)
            out.append(prediction)
            current = prediction.next_state
        return out

    def uncertainty(self, state: State, action: Action) -> Uncertainty:
        residual = getattr(self, "last_loss", 0.0)
        confidence = 1.0 / (1.0 + max(0.0, residual))
        return Uncertainty(epistemic=float(residual), aleatoric=0.0, confidence=confidence)

    def train(self, transitions: Iterable, epochs: int = 25, batch_size: int = 32) -> dict:
        transitions = list(transitions)
        if not transitions:
            raise ValueError("at least one transition is required")
        self._ensure(len(self._state_vec(transitions[0].state)))
        n = len(transitions)
        compute_device = self.training_device if n >= self.gpu_min_samples else self.device
        self._encoder.to(compute_device)
        self._net.to(compute_device)
        self._decoder.to(compute_device)
        self._optimizer = torch.optim.Adam(
            list(self._encoder.parameters())
            + list(self._net.parameters())
            + list(self._decoder.parameters()),
            lr=self.lr,
        )
        if compute_device.type == "cuda":
            torch.set_float32_matmul_precision("high")
        x = torch.tensor([self._state_vec(t.state) for t in transitions], dtype=torch.float32, device=compute_device)
        y = torch.tensor([self._state_vec(t.next_state) for t in transitions], dtype=torch.float32, device=compute_device)
        a = torch.tensor([self._action_vec(t.action) for t in transitions], dtype=torch.float32, device=compute_device)
        r = torch.tensor([float(t.reward) for t in transitions], dtype=torch.float32, device=compute_device)
        done = torch.tensor([float(t.done) for t in transitions], dtype=torch.float32, device=compute_device)
        final = 0.0
        generator = torch.Generator().manual_seed(self.seed)
        for _ in range(epochs):
            order = torch.randperm(n, generator=generator)
            for start in range(0, n, batch_size):
                idx = order[start : start + batch_size]
                if compute_device.type == "cuda":
                    idx = idx.to(compute_device)
                z = self._encoder(x[idx])
                nz, reward_pred, done_pred, next_state_pred = self._net(z, a[idx])
                loss = (
                    ((next_state_pred - y[idx]) ** 2).mean()
                    + 0.25 * ((reward_pred - r[idx]) ** 2).mean()
                    + 0.25 * (torch.sigmoid(done_pred) - done[idx]).pow(2).mean()
                )
                self._optimizer.zero_grad()
                loss.backward()
                self._optimizer.step()
                final = float(loss.item())
        self.last_loss = final
        self._encoder.to(self.device)
        self._net.to(self.device)
        self._decoder.to(self.device)
        self._optimizer = torch.optim.Adam(
            list(self._encoder.parameters())
            + list(self._net.parameters())
            + list(self._decoder.parameters()),
            lr=self.lr,
        )
        return {"loss": final, "epochs": epochs, "samples": n, "training_device": compute_device.type}

    @property
    def learnable(self) -> bool:
        return True
