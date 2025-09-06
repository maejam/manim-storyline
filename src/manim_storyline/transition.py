"""Transition between stories."""

import typing as t
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field

import manim as m  # type: ignore[import-untyped]
import manim.typing as mt  # type: ignore[import-untyped]
import numpy as np
import numpy.polynomial as npp

if t.TYPE_CHECKING:
    from .storyline import Story


class TransitionError(Exception):
    """Raised for all Transition related exceptions."""

    pass


@dataclass
class Transition(ABC):
    """The base class for all Transitions.

    Attributes
    ----------
    target_frame_display
        Can be a boolean or a Manim Animation class.
        - If ``True`` (the default): the frame will simply be added to the scene
        (usually before the camera shifts to the story, but this depends on the
        concrete class).
        implementing the transition).
        - If ``False``: the frame will not be displayed (nor added to the world).
        - If a ``manim.Animation``: the frame will be created using the chosen
        animation.
    zoom_out_margin
        The width of the margin that is added to the frame when zooming out.
    zoom_in_margin
        The width of the margin that is added to the frame when zooming in.
    """

    target_frame_display: bool | type[m.Animation] = True
    zoom_out_margin: float = 5
    zoom_in_margin: float = 2

    @abstractmethod
    def _transition(self, target: "Story") -> None:
        """Define the logic that is executed when transitionning.

        Do not call directly in client code. This method is called by
        ``StoryLineScene.transition_to``.

        Parameters
        ----------
        target
            The story to transition to.
        """
        self.scene = target.scene
        self.head = self.scene.head
        self.target = target

    def add_frame_to_scene(self, story: "Story") -> None:
        """Add the story frame to the scene and to the world.

        Parameters
        ----------
        story
            The story whose frame to add.
        """
        self.scene.add(story.frame)
        self.scene.add_to_world(story.frame)

    def zoom_in_on_story(self, story: "Story") -> m.Animation:
        """Zoom in on a story.

        Parameters
        ----------
        story
            The story to zoom in on.

        Returns
        -------
            The zoom in animation. This method does not play the animation so that
            the calling code can combine multiple animations if needed.
        """
        animation = self.scene.camera.auto_zoom(story.frame, margin=self.zoom_in_margin)  # pyright: ignore[reportAttributeAccessIssue]
        return animation

    def zoom_out_from_story(self, story: "Story") -> m.Animation:
        """Zoom out of a story.

        Parameters
        ----------
        story
            The story to zoom out of.

        Returns
        -------
            The zoom out animation. This method does not play the animation so that
            the calling code can combine multiple animations if needed.
        """
        animation = self.scene.camera.auto_zoom(  # pyright: ignore[reportAttributeAccessIssue]
            story.frame,
            margin=self.zoom_out_margin,
        )
        return animation

    def move_camera_frame_to(self, mobject: m.Mobject) -> m.Animation:
        """Move the camera frame.

        Parameters
        ----------
        mobject
            The Mobject to focus on.

        Returns
        -------
            The camera frame animation. This method does not play the animation so
            that the calling code can combine multiple animations if needed.
        """
        animation = self.scene.camera.frame.animate.move_to(mobject)  # pyright: ignore[reportAttributeAccessIssue]
        return animation

    def animate_frame_creation(self, story: "Story") -> m.Animation:
        """Animate the frame creation.

        Parameters
        ----------
        story
            The story whose frame creation should be animated.

        Returns
        -------
            The frame creation animation. This method does not play the animation so
            that the calling code can combine multiple animations if needed.

        Raises
        ------
        TransitionError
            If target_frame_display is a bool.
        """
        if type(self.target_frame_display) is bool:
            raise TransitionError(
                """`Transition.animate_frame_creation` should only be called when
                Transition.target_frame_display is a Manim Animation.
                Use `Transition.add_frame_to_scene` instead."""
            )
        animation = self.target_frame_display(story.frame)
        self.scene.add_to_world(story.frame)
        return animation


@dataclass
class Slide(Transition):
    """Slide from one story to another.

    Steps:
    - Display the target frame if needed.
    - Zoom out from the head story.
    - Slide to the target story.
    - Animate the target frame creation if needed.
    - Zoom in on the target story.

    Attributes
    ----------
    target_frame_display
        Can be a boolean or a Manim Animation class.
        - If ``True`` (the default): the frame will simply be added to the scene
        (usually before the camera shifts to the story, but this depends on the
        concrete class).
        implementing the transition).
        - If ``False``: the frame will not be displayed (nor added to the world).
        - If a ``manim.Animation``: the frame will be created using the chosen
        animation.
    zoom_out_margin
        The width of the margin that is added to the frame when zooming out.
    zoom_in_margin
        The width of the margin that is added to the frame when zooming in.
    """

    def _transition(self, target: "Story") -> None:
        """Define the slide transition steps.

        Parameters
        ----------
        story
            The story to slide to.
        """
        super()._transition(target)

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
        """Slide to a given story.

        Parameters
        ----------
        story
            The story to slide to.

        Returns
        -------
            The sliding animation. This method does not play the animation so
            that the calling code can combine multiple animations if needed.
        """
        animation = self.scene.camera.auto_zoom(  # pyright: ignore[reportAttributeAccessIssue]
            story.frame,
            margin=self.zoom_in_margin,
        )
        return animation


@dataclass
class FreeStoryLine(Transition):
    """Slide from one story to another with an arrow connecting the 2 stories.

    Useful to give the impression of a connection between the 2 stories.
    The arrow connecting the stories is not constrained in any way.
    A good placement of the story frames is essential to give a good result.

    Steps:
    - Display the target frame if needed.
    - Zoom out from the head story.
    - Display the line from the head frame to the head dot if needed and move the
    camera to the head dot.
    - Display the arrow from the head dot to the target dot if needed and move the
    camera to the target dot.
    - Display the line from the target dot to the target frame if needed and move
    the camera to the target frame.
    - Animate the target frame creation if needed.
    - Zoom in on the target story.

    Attributes
    ----------
    target_frame_display
        Can be a boolean or a Manim Animation class.
        - If ``True`` (the default): the frame will simply be added to the scene
        (usually before the camera shifts to the story, but this depends on the
        concrete class).
        implementing the transition).
        - If ``False``: the frame will not be displayed (nor added to the world).
        - If a ``manim.Animation``: the frame will be created using the chosen
        animation.
    zoom_out_margin
        The width of the margin that is added to the frame when zooming out.
    zoom_in_margin
        The width of the margin that is added to the frame when zooming in.
    display_head_dot
        Whether or not to display the head dot.
    display_target_dot
        Whether or not to display the target dot.
    display_arrow
        Whether or not to display the arrow.
    display_head2dot_line
        Whether or not to display the line from the head frame to its dot.
    display_dot2target_line
        Whether or not to display the line from the target dot to the target frame.
    arrow
        The manim.Arrow object to use. Defaults to the default manim arrow.
    head2dot_line
        The manim.Line object to use. Defaults to the default manim line.
    dot2target_line
        The manim.Arrow object to use. Defaults to the default manim line.
    dot2target_line_throuh
        A tuple of points for the dot2target line to pass through. Useful to
        give a nice result in some situations.
    """

    display_head_dot: bool = True
    display_target_dot: bool = True
    display_arrow: bool = True
    display_head2dot_line: bool = True
    display_dot2target_line: bool = True
    arrow: m.Arrow = field(default_factory=lambda: m.Arrow())
    head2dot_line: m.Line = field(default_factory=lambda: m.Line())
    dot2target_line: m.Line = field(default_factory=lambda: m.Line())
    dot2target_line_through: tuple[mt.Point3DLike, ...] = ()

    def _transition(self, target: "Story") -> None:
        """Define the FreeStoryLine transition steps.

        Parameters
        ----------
        story
            The story to transition to.
        """
        super()._transition(target)

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
        """Adjust the position of a given dot position relative to its story frame.

        Parameters
        ----------
        story
            The story whose dot needs adjusting.
        "in_or_out"
            Which dot to consider.

        Returns
        -------
            The dot in question for convenience.
        """
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
        """Animate the arrow.

        Parameters
        ----------
        start
            The starting point for the arrow.
        end
            The ending point for the arrow.

        Returns
        -------
            The arrow creation animation. This method does not play the animation so
            that the calling code can combine multiple animations if needed.
        """
        self.arrow.put_start_and_end_on(start.get_center(), end.get_center())
        animation = m.GrowArrow(self.arrow)
        self.scene.add_to_world(self.arrow)
        return animation

    def line_from_head_to_dot(self) -> m.Line:
        """Build the line from the head frame to the head out_dot.

        Returns
        -------
            The line object.
        """
        direction = self.head.out_dot_direction
        self.head2dot_line.put_start_and_end_on(
            self.head.frame.get_critical_point(direction),
            self.head.out_dot.get_center(),
        )
        self.scene.add_to_world(self.head2dot_line)
        return self.head2dot_line

    def line_from_dot_to_target(self, story: "Story") -> list[m.Line]:
        """Build the line(s) from the target in_dot to the target frame.

        The line(s) go from the target in_dot to the target frame passing through the
        `dot2target_line_through points.

        Returns
        -------
            A list containing the line object(s).
        """
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
    """Similar to FreeStoryLine but the arrow is constrained in the y direction.

    Useful to build a timeline like transition.
    """

    def adjust_dot_position(self, story: "Story", in_or_out: str) -> m.Dot:
        dot = super().adjust_dot_position(story, in_or_out)
        if story is self.target:
            dot.set_y(self.head.out_dot.get_y())
        else:
            dot.set_y(self.head.in_dot.get_y())
        return dot


@dataclass
class VerticalStoryLine(FreeStoryLine):
    """Similar to FreeStoryLine but the arrow is constrained in the x direction.

    Useful to build a tree like transition.
    """

    def adjust_dot_position(self, story: "Story", in_or_out: str) -> m.Dot:
        dot = super().adjust_dot_position(story, in_or_out)
        if story is self.target:
            dot.set_x(self.head.out_dot.get_x())
        else:
            dot.set_x(self.head.in_dot.get_x())
        return dot


@dataclass
class PolyFitStoryLine(FreeStoryLine):
    """Fit a polynomial through the out_dots of the given stories.

    Useful to give the impression of a smooth curve going through multiple stories.
    A good placement of the story frames and their respective out_dots is essential
    to give a good result.
    This transition still occurs between two stories (the head and a target) but
    in order to compute the polynomial function it needs to know all the stories
    from the beginning (``stories_to_include_in_polyfit`` parameter).

    Steps:
    - Fit the polynomial through all the dots first.
    - Display the target frame if needed.
    - Zoom out from the head story.
    - Display the line from the head frame to the head dot if needed and move the
    camera to the head dot.
    - Display the arrow from the head dot to the target dot if needed and move the
    camera to the target dot.
    - Display the line from the target dot to the target frame if needed and move
    the camera to the target frame.
    - Animate the target frame creation if needed.
    - Zoom in on the target story.

    Attributes
    ----------
    target_frame_display
        Can be a boolean or a Manim Animation class.
        - If ``True`` (the default): the frame will simply be added to the scene
        (usually before the camera shifts to the story, but this depends on the
        concrete class).
        implementing the transition).
        - If ``False``: the frame will not be displayed (nor added to the world).
        - If a ``manim.Animation``: the frame will be created using the chosen
        animation.
    zoom_out_margin
        The width of the margin that is added to the frame when zooming out.
    zoom_in_margin
        The width of the margin that is added to the frame when zooming in.
    display_head_dot
        Whether or not to display the head dot.
    display_target_dot
        Whether or not to display the target dot.
    display_arrow
        Whether or not to display the arrow.
    display_head2dot_line
        Whether or not to display the line from the head frame to its dot.
    display_dot2target_line
        Whether or not to display the line from the target dot to the target frame.
    arrow
        The manim.Arrow object to use. Defaults to the default manim arrow.
    head2dot_line
        The manim.Line object to use. Defaults to the default manim line.
    dot2target_line
        The manim.Arrow object to use. Defaults to the default manim line.
    dot2target_line_throuh
        A tuple of points for the dot2target line to pass through. Useful to
        give a nice result in some situations.
    stories_to_include_in_polyfit
        An iterable of story objects or story names to include in the fit.
        It is possible to mix objects and names. This parameter is optional but
        takes precedence over the ``stories_to_exclude_from_polyfit parameter``.
    stories_to_exclude_from_polyfit
        An iterable of story objects or story names to exclude from the fit relative
        to all the stories created in the scene. This parameter is optional. If none of
        ``stories_to_include_in_polyfit`` and ``stories_to_exclude_from_polyfit`` are
        defined, then all stories in the scene will be used for the fit.
    poly_degree
        The degree of the computed polynomial. Defaults to the number of stories - 1.
    arrow_tip
        The arrow tip object to use for the animation.
    poly
        The computed polynomial coefficients.
    """

    stories_to_include_in_polyfit: t.Iterable["str | Story"] = ()
    stories_to_exclude_from_polyfit: t.Iterable["str | Story"] = ()
    poly_degree: int | None = None
    arrow_tip: m.ArrowTip = field(
        default_factory=lambda: m.ArrowTriangleFilledTip(color=m.WHITE)
    )

    def __post_init__(self) -> None:
        self.poly: np.ndarray | None = None

    def _transition(self, target: "Story") -> None:
        """Define the transition steps.

        Parameters
        ----------
        story
            The story to transition to.
        """
        self.scene = target.scene
        self.stories = self.determine_stories_to_include()
        for story in self.stories:
            self.adjust_dot_position(story, "out")

        if self.poly is None:  # Fit once and for all
            degree = self.poly_degree or len(self.stories) - 1
            dots_coords = self.get_stories_dot_coords()
            self.poly = self.fit_polynomial(dots_coords["x"], dots_coords["y"], degree)
        super()._transition(target)

    def determine_stories_to_include(self) -> list["Story"]:
        """Determine the stories to include in the fit.

        Returns
        -------
            A list of story objects to include in the fit.
        """
        stories = []
        for story in self.stories_to_include_in_polyfit:
            try:
                stories.append(self.scene.stories[story])  # pyright: ignore[reportArgumentType]
            except KeyError:
                stories.append(story)
        if not stories:
            stories = list(self.scene.stories.values())
            for story in stories:
                if (
                    story in self.stories_to_exclude_from_polyfit
                    or story.name in self.stories_to_exclude_from_polyfit
                ):
                    stories.remove(story)
        print(list(story.name for story in stories))
        return stories

    def get_stories_dot_coords(self) -> dict[str, np.ndarray]:
        """Get the coordinates of the dots of the included stories for the fit.

        Only the out_dots are considered.

        Returns
        -------
            A dictionnary containing two arrays (the x values and the y values).
        """
        x = np.zeros(len(self.stories))
        y = np.zeros(len(self.stories))
        for num, story in enumerate(self.stories):
            dot_position = story.out_dot.get_center()
            x[num], y[num] = dot_position[0], dot_position[1]
        return {"x": x, "y": y}

    def fit_polynomial(self, x: np.ndarray, y: np.ndarray, degree: int) -> np.ndarray:
        """Fit the polynomial through the dots.

        Parameters
        ----------
        x
            The x values of the dots as returned by ``get_stories_dot_coords``.
        y
            The y values of the dots as returned by ``get_stories_dot_coords``.
        degree
            The degree of the polynomial to be fitted.

        Returns
        -------
            An array containing the polynomial coefficients in increasing degree order.
        """
        poly = npp.polynomial.polyfit(x, y, deg=degree)
        return poly

    def animate_arrow(self, start: m.Mobject, end: m.Mobject) -> m.Animation:
        """Animate the arrow made of the polynomial and an arrow tip.

        Parameters
        ----------
        start
            The starting point for the arrow.
        end
            The ending point for the arrow.

        Returns
        -------
            The polynomial creation animation. The tip is "stuck" to it via an updater
            function. This method does not play the animation so that the calling code
            can combine multiple animations if needed.
        """

        def poly(x: float) -> float:
            y = 0
            assert self.poly is not None  # make mypy and pyright happy :)
            for deg, coef in enumerate(self.poly):
                y += coef * x**deg
            return y

        # TODO: Aligning the arrow tip with the dots is tricky. This is just good enough
        f = m.ParametricFunction(
            lambda x: [x, poly(x), 0],  # pyright: ignore[reportArgumentType]
            t_range=[
                start.get_x(),
                end.get_x(m.RIGHT) - self.arrow_tip.length_over_dim(0),
                0.01,
            ],  # pyright: ignore[reportArgumentType]
        )

        def position_tip(tip: m.Mobject) -> None:
            """Position the tip and rotate it accordingly.

            The code for the rotation comes from the manim.mobject.geometry.arc
            source code.

            Parameter
            ---------
            tip
                The Mobject to be used for the tip.
            """
            handle = f.points[-2]
            anchor = f.get_end()
            angles = m.cartesian_to_spherical((handle - anchor).tolist())
            tip.rotate(
                angles[1] - m.PI - tip.tip_angle,
            ).move_to(f.get_end())

        self.arrow_tip.add_updater(position_tip)
        self.scene.add(self.arrow_tip)
        return m.Create(f)
