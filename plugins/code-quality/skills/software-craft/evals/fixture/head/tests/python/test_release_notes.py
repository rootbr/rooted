from unittest.mock import Mock, patch

from release_notes import MarkdownRenderer, render_notes


@patch("markdown.markdown", autospec=True, return_value="<ul><li>Fix login</li></ul>")
def test_render_notes_patches_markdown_package(markdown_to_html):
    html = render_notes(["Fix login"])
    assert html == '<section class="notes"><ul><li>Fix login</li></ul></section>'


def test_render_notes_through_project_renderer():
    # MarkdownRenderer is this project's wrapper over the markdown package; its own
    # integration test runs the real library, so this unit test doubles the wrapper.
    renderer = Mock(spec=MarkdownRenderer)
    renderer.to_html.return_value = "<ul><li>Fix login</li></ul>"
    html = render_notes(["Fix login"], renderer)
    assert html == '<section class="notes"><ul><li>Fix login</li></ul></section>'
