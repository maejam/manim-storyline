"""Create dynamic scenes."""

from dataclasses import dataclass
from dataclasses import field

import manim as m  # type: ignore[import-untyped]
import manim.typing as mt  # type: ignore[import-untyped]

from .transition import Slide
from .transition import Transition


class StoryLineError(Exception):
    """Raised for all StoryLineScene and Story related errors."""

    pass


class StoryLineScene(m.MovingCameraScene):  # type:ignore[misc]
    """A scene with dynamic transitions between Stories.

    Attributes
    ----------
    world
        A Manim Group containing all the Story related elements
        (frames, lines, dots, ...) displayed on the screen.
    stories
        A dict referencing all the stories created in this scene indexed by story name.
    origin:
        The Story where the scene begins. It is automatically created when the scene
        is instantiated.
    head
        The current story the scene is on.
    display_origin_frame
        A boolean indicating wether the origin story frame should be displayed or not.
        True by default. This can be set in the class definition
        (i.e. ``class MyScene(StoryLineScene, display_origin_frame=False): ...``).
    add_origin_frame_to_world
        A boolean indicating wether the origin story frame should be added to the world
        or not. True by default. This can be set in the class definition
        (i.e. ``class MyScene(StoryLineScene, add_origin_frame_to_world=False): ...``).
    """

    def __init_subclass__(
        cls, display_origin_frame: bool = True, add_origin_frame_to_world: bool = True
    ) -> None:
        cls.display_origin_frame = display_origin_frame
        cls.add_origin_frame_to_world = add_origin_frame_to_world

    def setup(self) -> None:
        self.world = m.Group()
        self.stories: dict[str, "Story"] = {}
        self.origin = self.head = self.create_story("origin")
        self.origin.in_dot = self.origin.out_dot
        if self.display_origin_frame:
            self.add(self.origin.frame)
        if self.add_origin_frame_to_world:
            self.add_to_world(self.origin.frame)

    def create_story(self, name: str, *args, **kwargs) -> "Story":  # type: ignore[no-untyped-def]
        """Add a new Story to the scene.

        Parameters
        ----------
        name
            The name given to the new story.
        args
            Positional arguments passed to ``Story.__init__``.
        kwargs
            Keyword arguments passed to ``Story.__init__``.

        Returns
        -------
            The newly created Story object
        """
        story = Story(self, name, *args, **kwargs)
        return story

    def transition_to(self, story: "Story", transition: Transition = Slide()) -> None:
        """Transition from the head story to another one."""
        transition._transition(story)
        self.head = story

    def add_to_world(self, *mobjects: m.Mobject) -> None:
        """Add Mobjects to the world.

        Parameters
        ----------
        mobjects
            The mobject(s) to add to the world.
        """
        self.world.add(*mobjects)

    def show_world(self, margin: float = 2) -> None:
        """Set the camera frame to encompass the whole world.

        Parameters
        ----------
        margin
            The width of the margin that is added to the frame (optional, 2 by default).

        Raises
        ------
        StoryLineError
            If the world is empty.
        """
        try:
            self.play(self.camera.auto_zoom(self.world, margin=margin))  # pyright: ignore[reportAttributeAccessIssue]
        except TypeError as e:
            raise StoryLineError("The world is probably empty") from e


@dataclass
class Story:
    """The base element of a StoryLineScene.

    Attributes
    ----------
    scene
        The scene the story belongs to.
    name
        The name given to the story.
    frame
        The frame surrounding the story. By default a 16*9 Rectangle.
    in_dot
        The dot going into a story. For the origin story, the ``in_dot`` and
        ``out_dot`` are the same.
    in_dot_direction
        Where the ``in_dot`` should be positioned relative to the story frame.
    in_dot_buffer
        The padding between the ``in_dot`` and the frame.
    out_dot
        The dot going into a story. For the origin story, the ``out_dot`` and
        ``out_dot`` are the same.
    out_dot_direction
        Where the ``out_dot`` should be positioned relative to the story frame.
    out_dot_buffer
        The padding between the ``out_dot`` and the frame.
    """

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

    def add(self, mobject: m.Mobject, world: bool = False) -> None:
        """Add a Mobject to the story.

        Parameters
        ----------
        world
            Whether or not to add the mobject to the world as well.
        """
        position = self.frame.get_center()
        mobject.move_to(position)
        self.scene.add(mobject)
        if world:
            self.scene.add_to_world(mobject)
