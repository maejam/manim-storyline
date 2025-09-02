import typing
from abc import ABC
from abc import abstractmethod

import manim as m

from .config import config

if typing.TYPE_CHECKING:
    from .storyline import Story
    from .storyline import StoryLineScene


class Transition(ABC):
    dot_x_value_constraint: bool = False
    dot_y_value_constraint: bool = False

    def __init__(self, target: "Story", scene: "StoryLineScene") -> None:
        self.scene = scene
        self.target = target
        self.head = scene.head

        # Set ambiguous config keys
        self.head.dot_position = config.head_dot_position  # pyright: ignore[reportAttributeAccessIssue]
        self.target.dot_position = config.target_dot_position  # pyright: ignore[reportAttributeAccessIssue]
        self.head.dot_buffer = config.head_dot_buffer  # pyright: ignore[reportAttributeAccessIssue]
        self.target.dot_buffer = config.target_dot_buffer  # pyright: ignore[reportAttributeAccessIssue]

    @abstractmethod
    def _transition(self) -> None:
        pass

    def add_frame_to_scene(self, story: "Story") -> None:
        self.scene.add(story.frame)

    def zoom_in_on_story(self, story: "Story") -> m.Animation:
        animation = self.scene.camera.auto_zoom(story.frame, margin=story.margin)  # pyright: ignore[reportAttributeAccessIssue]
        return animation

    def zoom_out_from_story(self, story: "Story") -> m.Animation:
        animation = self.scene.camera.auto_zoom(  # pyright: ignore[reportAttributeAccessIssue]
            story.frame,
            margin=story.margin * config.zoom_out_factor + config.zoom_out_margin,
        )
        return animation

    def move_camera_frame_to(self, mobject: m.Mobject) -> m.Animation:
        animation = self.scene.camera.frame.animate.move_to(mobject)  # pyright: ignore[reportAttributeAccessIssue]
        return animation

    def slide_to_story(self, story: "Story") -> m.Animation:
        animation = self.scene.camera.auto_zoom(  # pyright: ignore[reportAttributeAccessIssue]
            story.frame,
            margin=story.margin * config.zoom_in_factor + config.zoom_in_margin,
        )
        return animation

    def animate_frame_creation(self, story: "Story") -> m.Animation:
        return story.frame_display(story.frame)

    def add_dot_next_to_story(self, story):
        dot = m.Dot(
            radius=config.dot_radius,
            color=config.dot_color,
            fill_opacity=config.dot_opacity,
            stroke_width=config.dot_stroke_width,
        )
        dot.next_to(story.frame, story.dot_position, buff=story.dot_buffer)

        if self.dot_x_value_constraint and story is self.target:
            dot.set_x(self.head.dot.get_x())  # pyright: ignore[reportAttributeAccessIssue]
        if self.dot_y_value_constraint and story is self.target:
            dot.set_y(self.head.dot.get_y())  # pyright: ignore[reportAttributeAccessIssue]
        story.dot = dot
        self.scene.add_to_world(dot)
        return dot

    def animate_arrow(self, start: m.Mobject, end: m.Mobject) -> m.Animation:
        arrow = m.Arrow(start=start, end=end, buff=0)
        animation = m.GrowArrow(arrow)
        self.scene.add_to_world(arrow)
        return animation

    def line_from_story_to_dot(self, story) -> m.Line:
        line = (
            m.Line(story.frame.get_critical_point(story.dot_position), story.dot)
            if config.head2dot_line
            else m.Line(m.ORIGIN, m.ORIGIN)
        )
        self.scene.add_to_world(line)
        return line

    def line_from_dot_to_story(self, story) -> m.Line:
        line = (
            m.Line(story.dot, story.frame.get_critical_point(story.dot_position))
            if config.dot2target_line
            else m.Line(m.ORIGIN, m.ORIGIN)
        )
        self.scene.add_to_world(line)
        return line


class Slide(Transition):
    def _transition(self) -> None:
        if self.target.frame_display is True:
            self.add_frame_to_scene(self.target)
        self.scene.play(self.zoom_out_from_story(self.head))
        self.scene.play(self.slide_to_story(self.target))
        if self.target.frame_display and self.target.frame_display is not True:
            self.scene.play(self.animate_frame_creation(self.target))
        self.scene.play(self.zoom_in_on_story(self.target))


class FreeStoryLine(Transition):
    dot_x_value_constraint: bool = False
    dot_y_value_constraint: bool = False

    def _transition(self) -> None:
        if self.target.frame_display is True:
            self.add_frame_to_scene(self.target)
        self.scene.play(self.zoom_out_from_story(self.head))
        dot1 = self.add_dot_next_to_story(self.head)
        self.scene.play(
            m.Create(self.line_from_story_to_dot(self.head)),
            self.move_camera_frame_to(dot1),
        )
        self.scene.play(m.Create(dot1))
        dot2 = self.add_dot_next_to_story(self.target)
        self.scene.play(self.animate_arrow(dot1, dot2), self.move_camera_frame_to(dot2))
        self.scene.play(m.Create(dot2))
        self.scene.play(
            m.Create(self.line_from_dot_to_story(self.target)),
            self.move_camera_frame_to(self.target.frame),
        )
        if self.target.frame_display and self.target.frame_display is not True:
            self.scene.play(self.animate_frame_creation(self.target))
        self.scene.play(self.zoom_in_on_story(self.target))


class HorizontalStoryLine(FreeStoryLine):
    dot_y_value_constraint: bool = True


class VerticalStoryLine(FreeStoryLine):
    dot_x_value_constraint: bool = True
