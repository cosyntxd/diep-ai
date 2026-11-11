from dataclasses import dataclass
from typing import Any

import torch
from torch import Tensor


@dataclass
class ModelInputObject:
    object_type: int
    rel_position_x: float
    rel_position_y: float

    abs_velocity_x: float
    abs_velocity_y: float

    is_friendly: float
    team_encoding: tuple[bool, bool, bool, bool, bool]


@dataclass
class ModelInputs:
    exp: float
    position_x: float
    position_y: float

    vel_x: float
    vel_y: float

    # Upgrades: exactly 8 integers
    upgrades: tuple[int, int, int, int, int, int, int, int]

    time_since_shooting: float
    pointing_angle: float
    fov: float

    visible_objects: list[ModelInputObject]

    team_encoding: tuple[bool, bool, bool, bool, bool]
    gamemode_ffa: bool
    gamemode_4v4: bool

    def encode(self) -> Tensor:
        values = [
            self.exp,
            self.position_x,
            self.position_y,
            self.vel_x,
            self.vel_y,
            *self.upgrades,
            self.time_since_shooting,
            self.pointing_angle,
            self.fov,
            *self.team_encoding,
            self.gamemode_ffa,
            self.gamemode_4v4,
        ]

        return torch.tensor(values, dtype=torch.float32)


@dataclass
class ModelInputProcessed:
    ego: Tensor
    objects: list[tuple[int, Tensor]]


@dataclass
class ModelOutputs:
    pass
