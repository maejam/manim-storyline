import typing as t
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field

import manim as m  # type: ignore[import-untyped]
import manim.typing as mt  # type: ignore[import-untyped]
import numpy as np

if t.TYPE_CHECKING:
    from .storyline import Story
    from .storyline import StoryLineScene


class TransitionError(Exception):
    pass


@dataclass
class Transition(ABC):
    target_frame_display: bool | type[m.Animation] = True
    zoom_out_margin: float = 5
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
        animation = self.scene.camera.auto_zoom(story.frame, margin=self.zoom_in_margin)  # pyright: ignore[reportAttributeAccessIssue]
        return animation

    def zoom_out_from_story(self, story: "Story") -> m.Animation:
        animation = self.scene.camera.auto_zoom(  # pyright: ignore[reportAttributeAccessIssue]
            story.frame,
            margin=self.zoom_out_margin,
        )
        return animation

    def move_camera_frame_to(self, mobject: m.Mobject) -> m.Animation:
        animation = self.scene.camera.frame.animate.move_to(mobject)  # pyright: ignore[reportAttributeAccessIssue]
        return animation

    def animate_frame_creation(self, story: "Story") -> m.Animation:
        if type(self.target_frame_display) is bool:
            raise TransitionError(
                "`Transition.animate_frame_creation` should only be called when Transition.target_frame_display is a Manim Animation. Use `Transition.add_frame_to_scene` instead"
            )
        animation = self.target_frame_display(story.frame)
        self.scene.add_to_world(story.frame)
        return animation


@dataclass
class Slide(Transition):
    def _transition(self, target: "Story", scene: "StoryLineScene") -> None:
        super()._transition(target, scene)

        # Target frame add
        if self.target_frame_display is True:
            self.add_frame_to_scene(target)

        self.scene.play(self.zoom_out_from_story(self.head))
        self.scene.play(self.slide_to_story(target))

        # Target frame create
        if self.target_frame_display and self.target_frame_display is not True:
            self.scene.play(self.animate_frame_creation(target))

        self.scene.play(self.zoom_in_on_story(target))

    def slide_to_story(self, story: "Story") -> m.Animation:
        animation = self.scene.camera.auto_zoom(  # pyright: ignore[reportAttributeAccessIssue]
            story.frame,
            margin=self.zoom_in_margin,
        )
        return animation


@dataclass
class FreeStoryLine(Transition):
    display_head_dot: bool = True
    display_target_dot: bool = True
    display_arrow: bool = True
    display_head2dot_line: bool = True
    display_dot2target_line: bool = True
    arrow: m.Arrow = field(default_factory=lambda: m.Arrow())
    head2dot_line: m.Line = field(default_factory=lambda: m.Line())
    dot2target_line: m.Line = field(default_factory=lambda: m.Line())
    dot2target_line_through: tuple[mt.Point3DLike, ...] = ()

    def _transition(self, target: "Story", scene: "StoryLineScene") -> None:
        super()._transition(target, scene)

        # Target frame add
        if self.target_frame_display is True:
            self.add_frame_to_scene(target)

        self.scene.play(self.zoom_out_from_story(self.head))

        # Head to dot line
        dot1 = self.adjust_dot_position(self.head, "out")
        if self.display_head2dot_line:
            self.scene.play(
                m.Create(self.line_from_head_to_dot()),
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

        dot2 = self.adjust_dot_position(self.target, "in")

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
        if self.target_frame_display and self.target_frame_display is not True:
            self.scene.play(self.animate_frame_creation(target))
        self.scene.play(self.zoom_in_on_story(target))

    def adjust_dot_position(self, story: "Story", in_or_out: str) -> m.Dot:
        if in_or_out == "in":
            dot = story.in_dot
            direction = story.in_dot_direction
            buffer = story.in_dot_buffer
        else:
            dot = story.out_dot
            direction = story.out_dot_direction
            buffer = story.out_dot_buffer
        dot.next_to(story.frame, direction, buffer)
        return dot

    def animate_arrow(self, start: m.Mobject, end: m.Mobject) -> m.Animation:
        self.arrow.put_start_and_end_on(start.get_center(), end.get_center())
        animation = m.GrowArrow(self.arrow)
        self.scene.add_to_world(self.arrow)
        return animation

    def line_from_head_to_dot(self) -> m.Line:
        direction = self.head.out_dot_direction
        self.head2dot_line.put_start_and_end_on(
            self.head.frame.get_critical_point(direction),
            self.head.out_dot.get_center(),
        )
        self.scene.add_to_world(self.head2dot_line)
        return self.head2dot_line

    def line_from_dot_to_target(self, story: "Story") -> list[m.Line]:
        direction = self.target.in_dot_direction
        through = self.dot2target_line_through + (
            story.frame.get_critical_point(direction),
        )
        start = self.target.in_dot.get_center()
        lines: list[m.Line] = []
        for point in through:
            lines.append(self.dot2target_line.copy().put_start_and_end_on(start, point))
            start = point
        self.scene.add_to_world(self.dot2target_line)
        return lines


@dataclass
class HorizontalStoryLine(FreeStoryLine):
    def adjust_dot_position(self, story: "Story", in_or_out: str) -> m.Dot:
        dot = super().adjust_dot_position(story, in_or_out)
        if story is self.target:
            dot.set_y(self.head.out_dot.get_y())
        else:
            dot.set_y(self.head.in_dot.get_y())
        return dot


@dataclass
class VerticalStoryLine(FreeStoryLine):
    def adjust_dot_position(self, story: "Story", in_or_out: str) -> m.Dot:
        dot = super().adjust_dot_position(story, in_or_out)
        if story is self.target:
            dot.set_x(self.head.out_dot.get_x())
        else:
            dot.set_x(self.head.in_dot.get_x())
        return dot


@dataclass
class PolyFitStoryLine(FreeStoryLine):
    def get_stories_dot_coords(self) -> tuple[np.ndarray, np.ndarray]:
        x = np.array([])
        y = np.array([])
        for num, story in enumerate(self.scene.stories.values()):
            x[num] = story.dot.get_x()
            y[num] = story.dot.get_x()
        return x, y

    # def animate_arrow(self, start: m.Mobject, end: m.Mobject) -> m.Animation:
    #     poly = npp.Polynomial.fit(self.get_stories_dot_coords())
    #     print(poly)
    # self.arrow.put_start_and_end_on(start.get_center(), end.get_center())
    # animation = m.GrowArrow(self.arrow)
    # self.scene.add_to_world(self.arrow)
    # return animation
