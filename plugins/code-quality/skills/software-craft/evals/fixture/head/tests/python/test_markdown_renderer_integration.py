from release_notes import MarkdownRenderer


def test_markdown_renderer_renders_bullets_with_the_real_library():
    assert MarkdownRenderer().to_html("- Fix login") == "<ul>\n<li>Fix login</li>\n</ul>"
