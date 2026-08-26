"""Replay-based evaluation orchestration for perception metrics."""
from __future__ import annotations

from dataclasses import dataclass

from .gamestate import GameState
from .ground_truth import FrameGroundTruth
from .metrics import NumericMetric, classification_accuracy, numeric_metric


@dataclass(frozen=True)
class PerceptionEvaluation:
    hp: NumericMetric
    mp: NumericMetric
    player_x: NumericMetric
    player_y: NumericMetric
    map_accuracy: float | None


def evaluate(states: list[GameState], truth: dict[str, FrameGroundTruth]) -> PerceptionEvaluation:
    hp_actual: list[float] = []
    hp_expected: list[float] = []
    mp_actual: list[float] = []
    mp_expected: list[float] = []
    x_actual: list[float] = []
    x_expected: list[float] = []
    y_actual: list[float] = []
    y_expected: list[float] = []
    maps_actual: list[str | None] = []
    maps_expected: list[str | None] = []

    for state in states:
        expected = truth.get(state.observation_id)
        if expected is None:
            continue
        player = state.player
        if expected.hp is not None and player is not None and player.hp is not None:
            hp_actual.append(player.hp)
            hp_expected.append(expected.hp)
        if expected.mp is not None and player is not None and player.mp is not None:
            mp_actual.append(player.mp)
            mp_expected.append(expected.mp)
        if expected.player_x is not None and player is not None and player.x is not None:
            x_actual.append(player.x)
            x_expected.append(expected.player_x)
        if expected.player_y is not None and player is not None and player.y is not None:
            y_actual.append(player.y)
            y_expected.append(expected.player_y)
        if expected.map_name is not None:
            maps_expected.append(expected.map_name)
            maps_actual.append(state.map_name)

    return PerceptionEvaluation(
        hp=numeric_metric(hp_actual, hp_expected, 5),
        mp=numeric_metric(mp_actual, mp_expected, 5),
        player_x=numeric_metric(x_actual, x_expected, 1),
        player_y=numeric_metric(y_actual, y_expected, 1),
        map_accuracy=classification_accuracy(maps_actual, maps_expected),
    )
