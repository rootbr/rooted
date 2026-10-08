"""Tags and labels attached to catalogue items."""

DEFAULT_TAGS = []
DEFAULT_LABELS = ("draft",)


def add_tag(item, name, tags=DEFAULT_TAGS):
    """Append a tag to the item's tag list and return the list."""
    tags.append(name)
    item.tags = tags
    return tags


def labels_for(item, defaults=DEFAULT_LABELS):
    """The item's labels, or the immutable defaults when it has none."""
    return tuple(item.labels) if item.labels else defaults
