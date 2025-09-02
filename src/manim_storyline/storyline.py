import manim as m

from .transition import Slide
from .transition import Transition


class StoryLineScene(m.MovingCameraScene):
    def __init__(self, **kwargs):
        self.stories = {}
        self.world = m.VGroup()
        self.origin = self.head = self.create_story("origin")
        super().__init__(**kwargs)

    def create_story(
        self,
        name: str,
        frame: m.Mobject | None = None,
        frame_display: type[m.Animation] | bool = False,
        margin: float = 0,
    ) -> "Story":
        if not frame:
            frame = m.Rectangle(width=16, height=9)
        story = Story(
            self, name=name, frame=frame, frame_display=frame_display, margin=margin
        )
        self.stories[name] = story
        return story

    def transition_to(self, story: "Story", transition: type[Transition] = Slide):
        trans = transition(story, self)
        trans._transition()
        self.head = story

    def add_to_world(self, *mobjects: m.VMobject):
        self.world.add(mobjects)

    def show_world(self, margin: float = 2) -> None:
        self.play(self.camera.auto_zoom(self.world, margin=margin))  # pyright: ignore[reportAttributeAccessIssue]


class Story:
    def __init__(
        self,
        scene: "StoryLineScene",
        **kwargs,
    ) -> None:
        self.scene = scene
        self.name = kwargs["name"]
        self.frame = kwargs["frame"]
        self.frame_display = kwargs["frame_display"]
        self.margin = kwargs["margin"]
        self.scene.add_to_world(self.frame)

    def add(self, mobject: m.Mobject):
        position = self.frame.get_center()
        mobject.move_to(position)


def add_to_story(mobject, story):
    story.add(mobject)
    return mobject


m.Mobject.add_to_story = add_to_story  # pyright: ignore[reportAttributeAccessIssue]
