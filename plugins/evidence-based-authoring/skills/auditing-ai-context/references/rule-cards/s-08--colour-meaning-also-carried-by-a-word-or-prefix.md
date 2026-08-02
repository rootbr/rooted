---
title: Meaning that colour carries is also carried by a word or a prefix
rule_id: S-08
applies_to_target: [answer]
check_kind: mechanical
severity_default: medium
---

# Meaning that colour carries is also carried by a word or a prefix

## Thesis
Where colour marks a distinction — passing against failing, added against removed, one series against another — the same distinction is also available as text on the same row: a word, a prefix, or a symbol.

## Rationale
Colour is not a channel every reader receives. The conformance criterion is normative and sits at the standard's lowest conformance level, Level A: "Color is not used as the only visual means of conveying information, indicating an action, prompting a response, or distinguishing a visual element", with the associated technique "Ensuring that information conveyed by color differences is also available in text". A reader with a colour-vision deficiency, a monochrome terminal, a transcript piped to a file, or a client that strips escape sequences receives the text and not the colour, so a colour-only distinction reaches that reader as no distinction at all. A second and weaker reason applies to shading and saturation alone: in a hypothesized ordering of elementary perceptual tasks by the accuracy with which quantities are extracted, shading and colour saturation sit last of six.

## Example
```
bad:  a check list where only red and green separate the failing rows from the passing
good: "FAIL" and "PASS" printed on each row, with colour added on top
```

## Limits
Covers colour used as the sole carrier of a distinction. Colour layered on top of a word, prefix, or symbol is in scope to keep — the criterion governs information carried, not decoration. The second reason reaches shading and saturation only, and only as a hypothesis: colour hue is excluded from that ordering as a categorical encoding, saturation was ranked but never shown to a subject, and neither may be cited for hue or as a measured result.

## Validator
Find every place a distinction rides on colour alone: a diff-style block whose lines carry no `+`/`-` prefix, a status token that is coloured but unlabelled, a legend keyed by colour name, a series identified only by its colour. For each, check whether a word, prefix, or symbol repeats the distinction as text on the same row, and propose the missing token where it is absent.

## Patch output
When auditing an answer where colour is the only carrier of a distinction, emit one patch (`rule_id: S-08`, `location` set to the block and line hint, `current` = the colour-only row, `proposed` = the same row with the word, prefix, or symbol added, severity medium). Presence or absence of a text token is decidable from the answer itself, so no `needs_human` flag in the clear case.

## Source
WCAG 2.2, Success Criterion 1.4.1 *Use of Color*, Level A — "Color is not used as the only visual means of conveying information, indicating an action, prompting a response, or distinguishing a visual element"; technique G14, ensuring that information conveyed by colour differences is also available in text (<https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html>). Second, hypothesized reason confined to shading and saturation: Cleveland & McGill 1984, *JASA* 79(387):531–554, doi:10.1080/01621459.1984.10478080 — p. 536 hypothesizes the ordering of the elementary perceptual tasks and places shading and colour saturation last of six; hue is excluded at p. 532 as categorical and saturation was never illustrated to a subject.
