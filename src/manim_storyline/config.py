from dataclasses import dataclass

import manim as m
import manim.typing as mt


@dataclass
class Config:
    head_dot_position: (
        mt.Vector3D
    )  # Cannot initiate dot_position with mutable default value
    target_dot_position: (
        mt.Vector3D
    )  # Cannot initiate dot_position with mutable default value
    zoom_out_margin: float = 2
    zoom_in_margin: float = 2
    zoom_out_factor: float = 3
    zoom_in_factor: float = 3
    head_dot_buffer: float = 5
    target_dot_buffer: float = 5
    dot_radius: float = m.DEFAULT_DOT_RADIUS
    dot_color: m.ParsableManimColor = m.WHITE
    dot_opacity: float = 1
    dot_stroke_width: float = 0
    head2dot_line: bool = True
    dot2target_line: bool = True


config = Config(head_dot_position=m.DOWN, target_dot_position=m.DOWN)
