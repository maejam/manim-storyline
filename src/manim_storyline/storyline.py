import typing as t

import manim as m  # type: ignore[import-untyped]
from typing_extensions import Unpack

from .transition import Slide
from .transition import Transition


class StoryLineScene(m.MovingCameraScene):  # type:ignore[misc]
    def setup(self) -> None:
        self.world = m.VGroup()
        self.origin = self.head = self.create_story("origin")

    def create_story(
        self,
        name: str,
        frame: m.VMobject | None = None,
        frame_display: type[m.Animation] | bool = False,
        margin: float = 0,
    ) -> "Story":
        if not frame:
            frame = m.Rectangle(width=16, height=9)
        story = Story(
            self, name=name, frame=frame, frame_display=frame_display, margin=margin
        )
        return story

    def transition_to(self, story: "Story", transition: Transition = Slide()) -> None:
        transition._transition(story, self)
        self.head = story

    def add_to_world(self, *mobjects: m.VMobject) -> None:
        self.world.add(mobjects)

    def show_world(self, margin: float = 2) -> None:
        self.play(self.camera.auto_zoom(self.world, margin=margin))  # pyright: ignore[reportAttributeAccessIssue]


class StoryParams(t.TypedDict):
    name: str
    frame: m.VMobject
    frame_display: type[m.Animation] | bool
    margin: float


class Story:
    def __init__(
        self,
        scene: "StoryLineScene",
        **kwargs: Unpack[StoryParams],
    ) -> None:
        """
        DO NOT USE DIRECTLY, use the `StoryLine.create_story` factory method instead
        """
        self.scene = scene
        self.name = kwargs["name"]
        self.frame = kwargs["frame"]
        self.frame_display = kwargs["frame_display"]
        self.margin = kwargs["margin"]

    def add(self, mobject: m.Mobject) -> None:
        position = self.frame.get_center()
        mobject.move_to(position)


def add_to_story(mobject: m.Mobject, story: Story) -> m.Mobject:
    story.add(mobject)
    return mobject


m.Mobject.add_to_story = add_to_story  # pyright: ignore[reportAttributeAccessIssue]
