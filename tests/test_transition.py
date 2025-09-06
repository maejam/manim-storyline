import pytest

from manim_storyline import PolyFitStoryLine
from manim_storyline import StoryLineScene


@pytest.fixture
def scene():
    s = StoryLineScene()
    s.__init_subclass__()
    s.setup()
    return s


@pytest.fixture
def story1(scene):
    s = scene.create_story("story1")
    return s


@pytest.fixture
def story2(scene):
    s = scene.create_story("story2")
    return s


@pytest.fixture
def story3(scene):
    s = scene.create_story("story3")
    return s


def test_determine_stories_to_include_with_no_include_no_exclude(
    scene, story1, story2, story3
):
    pfsl = PolyFitStoryLine()
    pfsl.setup(story1)
    stories = pfsl.determine_stories_to_include()
    assert len(stories) == 4
    assert scene.origin in stories
    assert story1 in stories
    assert story2 in stories
    assert story3 in stories


def test_determine_stories_to_include_with_include_only(scene, story1, story2, story3):
    pfsl = PolyFitStoryLine(stories_to_include_in_polyfit=(story1, story2))
    pfsl.setup(story1)
    stories = pfsl.determine_stories_to_include()
    assert len(stories) == 2
    assert scene.origin not in stories
    assert story1 in stories
    assert story2 in stories
    assert story3 not in stories


def test_determine_stories_to_include_with_exclude_only(scene, story1, story2, story3):
    pfsl = PolyFitStoryLine(stories_to_exclude_from_polyfit=(story1, story2))
    pfsl.setup(story1)
    stories = pfsl.determine_stories_to_include()
    assert len(stories) == 2
    assert scene.origin in stories
    assert story1 not in stories
    assert story2 not in stories
    assert story3 in stories


def test_determine_stories_to_include_with_include_and_exclude(
    scene, story1, story2, story3
):
    pfsl = PolyFitStoryLine(
        stories_to_include_in_polyfit=(story1,),
        stories_to_exclude_from_polyfit=(story1, story2),
    )
    pfsl.setup(story1)
    stories = pfsl.determine_stories_to_include()
    assert len(stories) == 1
    assert scene.origin not in stories
    assert story1 in stories
    assert story2 not in stories
    assert story3 not in stories


def test_determine_stories_to_include_with_include_only_mixing_stories_and_str(
    scene, story1, story2, story3
):
    pfsl = PolyFitStoryLine(stories_to_include_in_polyfit=(story1, "story2"))
    pfsl.setup(story1)
    stories = pfsl.determine_stories_to_include()
    assert len(stories) == 2
    assert scene.origin not in stories
    assert story1 in stories
    assert story2 in stories
    assert story3 not in stories


def test_determine_stories_to_include_with_exclude_only_mixing_stories_and_str(
    scene, story1, story2, story3
):
    pfsl = PolyFitStoryLine(stories_to_exclude_from_polyfit=("story1", story2))
    pfsl.setup(story1)
    stories = pfsl.determine_stories_to_include()
    assert len(stories) == 2
    assert scene.origin in stories
    assert story1 not in stories
    assert story2 not in stories
    assert story3 in stories
