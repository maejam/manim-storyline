import typing as t
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field

import manim as m  # type: ignore[import-untyped]
import manim.typing as mt  # type: ignore[import-untyped]

if t.TYPE_CHECKING:
    from .storyline import Story
    from .storyline import StoryLineScene


@dataclass
class Transition(ABC):
    zoom_out_margin: float = 2
    zoom_in_margin: float = 2

    @abstractmethod
    def _transition(self, target: "Story", scene: "StoryLineScene") -> None:
        self.scene = scene
        self.head = self.scene.head
        self.target = target

    def add_frame_to_scene(self, story: "Story") -> None:
        self.scene.add(story.frame)
        self.scene.add_to_world(story.frame)

    def zoom_in_on_story(self, story: "Story") -> m.Animation:
        animation = self.scene.camera.auto_zoom(story.frame, margin=story.margin)  # pyright: ignore[reportAttributeAccessIssue]
        return animation

    def zoom_out_from_story(self, story: "Story") -> m.Animation:
        animation = self.scene.camera.auto_zoom(  # pyright: ignore[reportAttributeAccessIssue]
            story.frame,
            margin=story.margin + self.zoom_out_margin,
        )
        return animation

    def move_camera_frame_to(self, mobject: m.Mobject) -> m.Animation:
        animation = self.scene.camera.frame.animate.move_to(mobject)  # pyright: ignore[reportAttributeAccessIssue]
        return animation

    def animate_frame_creation(self, story: "Story") -> m.Animation:
        if type(story.frame_display) is bool:
            raise TypeError(
                "`Transition.animate_frame_creation` should only be called when Story.frame_display is a Manim Animation. Use `Transition.add_frame_to_scene` instead"
            )
        animation = story.frame_display(story.frame)
        self.scene.add_to_world(story.frame)
        return animation


@dataclass
class Slide(Transition):
    def _transition(self, target: "Story", scene: "StoryLineScene") -> None:
        super()._transition(target, scene)

        # Target frame add
        if target.frame_display is True:
            self.add_frame_to_scene(target)

        self.scene.play(self.zoom_out_from_story(self.head))
        self.scene.play(self.slide_to_story(target))

        # Target frame create
        if target.frame_display and target.frame_display is not True:
            self.scene.play(self.animate_frame_creation(target))

        self.scene.play(self.zoom_in_on_story(target))

    def slide_to_story(self, story: "Story") -> m.Animation:
        animation = self.scene.camera.auto_zoom(  # pyright: ignore[reportAttributeAccessIssue]
            story.frame,
            margin=story.margin + self.zoom_in_margin,
        )
        return animation


@dataclass
class FreeStoryLine(Transition):
    display_head_dot: bool = True
    display_target_dot: bool = True
    display_arrow: bool = True
    display_head2dot_line: bool = True
    display_dot2target_line: bool = True
    head_dot: m.Dot = field(default_factory=lambda: m.Dot())
    target_dot: m.Dot = field(default_factory=lambda: m.Dot())
    arrow: m.Arrow = field(default_factory=lambda: m.Arrow())
    head2dot_line: m.Line = field(default_factory=lambda: m.Line())
    dot2target_line: m.Line = field(default_factory=lambda: m.Line())
    dot2target_line_through: tuple[mt.Point3DLike, ...] = ()
    head_dot_direction: mt.Vector3D = field(default_factory=lambda: m.DOWN)
    head_dot_buffer: float = 5
    target_dot_direction: mt.Vector3D = field(default_factory=lambda: m.DOWN)
    target_dot_buffer: float = 5

    _dot_x_value_constraint: bool = False
    _dot_y_value_constraint: bool = False

    def _transition(self, target: "Story", scene: "StoryLineScene") -> None:
        super()._transition(target, scene)

        # Target frame add
        if target.frame_display is True:
            self.add_frame_to_scene(target)

        self.scene.play(self.zoom_out_from_story(self.head))
        dot1 = self.add_dot_next_to_story(self.head)

        # Head to dot line
        if self.display_head2dot_line:
            self.scene.play(
                m.Create(self.line_from_head_to_dot(self.head)),
                self.move_camera_frame_to(dot1),
            )
        else:
            self.scene.play(
                self.move_camera_frame_to(dot1),
            )

        # Head dot
        if self.display_head_dot:
            self.scene.play(m.Create(dot1))
            self.scene.add_to_world(dot1)

        dot2 = self.add_dot_next_to_story(target)

        # Arrow
        if self.display_arrow:
            self.scene.play(
                self.animate_arrow(dot1, dot2), self.move_camera_frame_to(dot2)
            )
        else:
            self.scene.play(self.move_camera_frame_to(dot2))

        # Target dot
        if self.display_target_dot:
            self.scene.play(m.Create(dot2))
            self.scene.add_to_world(dot2)

        # Dot to target line(s)
        if self.display_dot2target_line:
            for line in self.line_from_dot_to_target(target):
                self.scene.play(
                    m.Create(line),
                    self.scene.camera.frame.animate.shift(line.get_vector()),  # pyright: ignore[reportAttributeAccessIssue]
                )
                self.move_camera_frame_to(target.frame)
        else:
            self.scene.play(
                self.move_camera_frame_to(target.frame),
            )

        # Target frame create
        if target.frame_display and target.frame_display is not True:
            self.scene.play(self.animate_frame_creation(target))
        self.scene.play(self.zoom_in_on_story(target))

    def add_dot_next_to_story(self, story: "Story") -> m.Dot:
        if story is self.head:
            dot = self.head_dot
            direction = self.head_dot_direction
            buffer = self.head_dot_buffer
        else:
            dot = self.target_dot
            direction = self.target_dot_direction
            buffer = self.target_dot_buffer

        dot.next_to(story.frame, direction, buff=buffer)

        if self._dot_x_value_constraint and story is self.target:
            dot.set_x(self.head_dot.get_x())
        if self._dot_y_value_constraint and story is self.target:
            dot.set_y(self.head_dot.get_y())
        return dot

    def animate_arrow(self, start: m.Mobject, end: m.Mobject) -> m.Animation:
        self.arrow.put_start_and_end_on(start.get_center(), end.get_center())
        animation = m.GrowArrow(self.arrow)
        self.scene.add_to_world(self.arrow)
        return animation

    def line_from_head_to_dot(self, story: "Story") -> m.Line:
        direction = self.head_dot_direction
        self.head2dot_line.put_start_and_end_on(
            story.frame.get_critical_point(direction), self.head_dot.get_center()
        )
        self.scene.add_to_world(self.head2dot_line)
        return self.head2dot_line

    def line_from_dot_to_target(self, story: "Story") -> list[m.Line]:
        direction = self.target_dot_direction
        through = self.dot2target_line_through + (
            story.frame.get_critical_point(direction),
        )
        start = self.target_dot.get_center()
        lines: list[m.Line] = []
        for point in through:
            lines.append(self.dot2target_line.copy().put_start_and_end_on(start, point))
            start = point
        self.scene.add_to_world(self.dot2target_line)
        return lines


@dataclass
class HorizontalStoryLine(FreeStoryLine):
    _dot_y_value_constraint: bool = True


@dataclass
class VerticalStoryLine(FreeStoryLine):
    _dot_x_value_constraint: bool = True


@dataclass
class BezierStoryLine(FreeStoryLine):
    def animate_arrow(self, start: m.Mobject, end: m.Mobject) -> m.Animation:
        animation = m.Create(
            m.CubicBezier(
                start.get_center(),
                start.get_center() + m.RIGHT + m.DOWN,
                end.get_center(),
                end.get_center() + m.LEFT + m.UP,
            )
        )
        # self.arrow.put_start_and_end_on(start.get_center(), end.get_center())
        # animation = m.GrowArrow(self.arrow)
        # self.scene.add_to_world(self.arrow)
        return animation
