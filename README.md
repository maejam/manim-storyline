# manim-storyline

A plugin for [manim CE](https://github.com/ManimCommunity/manim) to build dynamic transitions between "stories" (subscenes) within a scene. The idea for this plugin was inspired by [manim-timeline](https://github.com/johnHostetter/manim-timeline) but it does not rely on [manim-slides](https://github.com/jeertmans/manim-slides) and it implements different kinds of transitions.

Currently 4 transitions are available:
- Slide: simply slide from one story to another.
- HorizontalStoryline: similar to manim-timeline.
- VerticalStoryLine: similar to manim-timeline but in the vertical direction.
- FreeStoryLine: unconstrained story line.
- PolyFitStoryLine: fit a polynomial story line between your stories (functional but needs some more work).

## Example

[![Watch the video](https://raw.githubusercontent.com/maejam/manim-storyline/main/examples/thumb.png)](https://raw.githubusercontent.com/maejam/manim-storyline/main/examples/example1.mp4)


```python
import manim as m

from manim_storyline import (
    StoryLineScene,
    Slide,
    HorizontalStoryLine,
    VerticalStoryLine,
)


class Test(StoryLineScene):
    def construct(self):
        # The "origin" story is created when instantiating the scene
        self.origin.add(m.Text("Origin"))

        # Create another story, position it and slide to it (default transition)
        story1 = self.create_story("story1")
        story1.frame.next_to(self.origin.frame, m.RIGHT * 30)
        self.transition_to(story1)
        story1.add(m.Text("story1"))

        # Create 3 more stories
        story2 = self.create_story("story2")
        story2.frame = m.Circle(radius=4.5)  # Customize anything
        story2.frame.next_to(story1.frame, m.RIGHT * 30)

        story3 = self.create_story("story3")
        story3.frame.next_to(story2.frame, m.RIGHT * 30)

        story4 = self.create_story("story4")
        story4.frame.next_to(story3.frame, m.UP * 30)

        # Adjust the position of the dots going in and out of the stories
        # for best result.
        story3.out_dot_direction = m.RIGHT
        story3.out_dot = m.Star(outer_radius=0.2)
        story4.in_dot_direction = m.RIGHT

        self.transition_to(story2, HorizontalStoryLine())
        story2.add(m.Text("story2"))
        self.transition_to(story3, HorizontalStoryLine())
        story3.add(m.Text("story3"))
        self.transition_to(story4, VerticalStoryLine())
        s4 = m.Text("story4")
        story4.add(s4)
        self.play(m.Write(s4))

        self.show_world(margin=5)
        self.wait(2)
```
