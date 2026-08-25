"""Learnable latent world model used by M1 and prepared for M2 imagination."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Sequence

from ..core.types import LatentState, Prediction, State, Action, Uncertainty

try:
    import torch
    from torch import nn
except ImportError:  # pragma: no cover
    torch = None
    nn = None


class _DynamicsNet(nn.Module):
    def __init__(self, state_dim: int, action_dim: int, latent_dim: int, hidden: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(latent_dim + action_dim, hidden), nn.Tanh(),
            nn.Linear(hidden, hidden), nn.Tanh(),
        )
        self.next_latent = nn.Linear(hidden, latent_dim)
        self.reward = nn.Linear(hidden, 1)
        self.done = nn.Linear(hidden, 1)
        self.state_head = nn.Linear(latent_dim, state_dim)

    def forward(self, z, a):
        h = self.net(torch.cat([z, a], dim=-1))
        nz = self.next_latent(h)
        return nz, self.reward(h).squeeze(-1), self.done(h).squeeze(-1), self.state_head(nz)


class LatentWorldModel:
    """Small PyTorch latent dynamics model.

    It learns next latent state, reward and terminal probability from transitions.
    The public API remains compatible with the original M1 backend.
    """
    def __init__(self, state_dim: int | None = None, action_dim: int = 3,
                 latent_dim: int = 8, hidden: int = 64, seed: int = 42, lr: float = 1e-3,
                 device: str | None = None):
        if torch is None:
            raise RuntimeError("PyTorch is required for the learnable LatentWorldModel")
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.latent_dim = latent_dim
        self.hidden = hidden
        self.seed = seed
        self.lr = lr
        requested = device or "auto"
        if requested == "auto":
            requested = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(requested)
        if self.device.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA device requested but CUDA is unavailable")
        self._net = None
        self._optimizer = None

    def _ensure(self, state_dim: int):
        if self._net is not None:
            return
        torch.manual_seed(self.seed)
        self.state_dim = state_dim
        self._encoder = nn.Sequential(nn.Linear(state_dim, self.hidden), nn.Tanh(), nn.Linear(self.hidden, self.latent_dim))
        self._net = _DynamicsNet(state_dim, self.action_dim, self.latent_dim, self.hidden)
        self._decoder = nn.Linear(self.latent_dim, state_dim)
        self._encoder.to(self.device); self._net.to(self.device); self._decoder.to(self.device)
        self._optimizer = torch.optim.Adam(list(self._encoder.parameters()) + list(self._net.parameters()) + list(self._decoder.parameters()), lr=self.lr)

    @staticmethod
    def _state_vec(state: State):
        return [float(x) for x in state.features]

    def _action_vec(self, action: Action):
        # Keep action encoding deterministic and compact; numeric delta/reward are useful
        # for the existing sandbox, while the id contributes a stable scalar hash.
        p = action.parameters
        vals = [((sum(map(ord, action.id)) % 997) / 997.0), float(p.get("delta", 0.0)), float(p.get("reward", 0.0))]
        if self.action_dim > 3:
            vals += [0.0] * (self.action_dim - 3)
        return vals[:self.action_dim]

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
            _, r, _, _ = self._net(z, a)
        return float(r.item())

    def predict(self, state: State, action: Action) -> Prediction:
        self._ensure(len(self._state_vec(state)))
        with torch.no_grad():
            x = torch.tensor([self._state_vec(state)], dtype=torch.float32, device=self.device)
            z = self._encoder(x)
            a = torch.tensor([self._action_vec(action)], dtype=torch.float32, device=self.device)
            nz, r, d, nx = self._net(z, a)
        next_state = State(tuple(float(v) for v in nx[0].tolist()), state.timestamp + 1, state.scenario_id, state.metadata)
        return Prediction(next_state, float(r.item()), float(torch.sigmoid(d).item()), float(r.item()))

    def rollout_latent(self, latent: LatentState, actions: Sequence[Action]):
        out=[]; z=latent
        for action in actions:
            z=self.predict_latent(z, action); out.append(z)
        return out

    def rollout(self, state: State, actions: Sequence[Action]):
        out=[]; current=state
        for action in actions:
            p=self.predict(current, action); out.append(p); current=p.next_state
        return out

    def uncertainty(self, state: State, action: Action) -> Uncertainty:
        # Single-model epistemic uncertainty is not identifiable; use confidence from
        # prediction residual statistics after training.
        residual = getattr(self, "last_loss", 0.0)
        confidence = 1.0 / (1.0 + max(0.0, residual))
        return Uncertainty(epistemic=float(residual), aleatoric=0.0, confidence=confidence)

    def train(self, transitions: Iterable, epochs: int = 25, batch_size: int = 32) -> dict:
        transitions=list(transitions)
        if not transitions:
            raise ValueError("at least one transition is required")
        self._ensure(len(self._state_vec(transitions[0].state)))
        x=torch.tensor([self._state_vec(t.state) for t in transitions], dtype=torch.float32, device=self.device)
        y=torch.tensor([self._state_vec(t.next_state) for t in transitions], dtype=torch.float32, device=self.device)
        a=torch.tensor([self._action_vec(t.action) for t in transitions], dtype=torch.float32, device=self.device)
        r=torch.tensor([float(t.reward) for t in transitions], dtype=torch.float32, device=self.device)
        done=torch.tensor([float(t.done) for t in transitions], dtype=torch.float32, device=self.device)
        n=len(transitions); final=0.0
        g=torch.Generator().manual_seed(self.seed)
        for _ in range(epochs):
            order=torch.randperm(n, generator=g)
            for start in range(0,n,batch_size):
                idx=order[start:start+batch_size]
                z=self._encoder(x[idx])
                nz, rp, dp, yp=self._net(z,a[idx])
                loss=((yp-y[idx])**2).mean() + 0.25*((rp-r[idx])**2).mean() + 0.25*(torch.sigmoid(dp)-done[idx]).pow(2).mean()
                self._optimizer.zero_grad(); loss.backward(); self._optimizer.step(); final=float(loss.item())
        self.last_loss=final
        return {"loss": final, "epochs": epochs, "samples": n}

    @property
    def learnable(self):
        return True
