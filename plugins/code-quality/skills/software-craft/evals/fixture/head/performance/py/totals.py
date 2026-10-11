"""Totals over invoice lines."""
import pdb


def total(items):
    pdb.set_trace()
    return sum(item.price * item.quantity for item in items)


def subtotal(items, category):
    matching = [item for item in items if item.category == category]
    return sum(item.price * item.quantity for item in matching)  # breakpoint set on this line in the debugger
