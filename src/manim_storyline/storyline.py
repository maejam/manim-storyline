from dataclasses import dataclass
from dataclasses import field

import manim as m  # type: ignore[import-untyped]
import manim.typing as mt  # type: ignore[import-untyped]

from .transition import Slide
from .transition import Transition


class StoryLineException(Exception):
    pass


class StoryLineScene(m.MovingCameraScene):  # type:ignore[misc]
    def setup(self) -> None:
        self.world = m.Group()
        self.stories: dict[str, "Story"] = {}
        self.origin = self.head = self.create_story("origin")
        self.origin.in_dot = self.origin.out_dot

    def create_story(self, name: str, *args, **kwargs) -> "Story":  # type: ignore[no-untyped-def]
        # TODO: find a way to type method without repeating dataclass signature (using fields?)
        story = Story(self, name, *args, **kwargs)
        return story

    def transition_to(self, story: "Story", transition: Transition = Slide()) -> None:
        transition._transition(story, self)
        self.head = story

    def add_to_world(self, *mobjects: m.Mobject) -> None:
        self.world.add(*mobjects)

    def show_world(self, margin: float = 2) -> None:
        try:
            self.play(self.camera.auto_zoom(self.world, margin=margin))  # pyright: ignore[reportAttributeAccessIssue]
        except TypeError as e:
            raise StoryLineException("The world is probably empty") from e


@dataclass
class Story:
    scene: StoryLineScene
    name: str
    frame: m.VMobject = field(default_factory=lambda: m.Rectangle(width=16, height=9))
    in_dot: m.Dot = field(default_factory=lambda: m.Dot())
    in_dot_direction: mt.Vector3D = field(default_factory=lambda: m.DOWN)
    in_dot_buffer: float = 5
    out_dot: m.Dot = field(default_factory=lambda: m.Dot())
    out_dot_direction: mt.Vector3D = field(default_factory=lambda: m.DOWN)
    out_dot_buffer: float = 5

    def __post_init__(self) -> None:
        self.scene.stories[self.name] = self

    def add(self, mobject: m.Mobject) -> None:
        position = self.frame.get_center()
        mobject.move_to(position)


def add_to_story(mobject: m.Mobject, story: Story) -> m.Mobject:
    story.add(mobject)
    return mobject


m.Mobject.add_to_story = add_to_story  # pyright: ignore[reportAttributeAccessIssue]
