"""Release notes rendered to HTML for the changelog page."""
import markdown


class MarkdownRenderer:
    """The project's own seam over the markdown package: callers depend on to_html, and
    test_markdown_renderer_integration.py runs it against the real library."""

    def to_html(self, text: str) -> str:
        return markdown.markdown(text)


def render_notes(entries, renderer=None):
    renderer = renderer or MarkdownRenderer()
    body = renderer.to_html("\n".join(f"- {entry}" for entry in entries))
    return f'<section class="notes">{body}</section>'
