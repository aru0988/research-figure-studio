---
name: research-figure-studio
description: Create and iteratively improve editable scientific architecture diagrams and result charts from method descriptions, code, reference figures, and screenshot feedback. Use for research-figure design, scientific palettes, model structure diagrams, 科研绘图、论文配图、配色优化 and structure/layout corrections. Produces vector artwork and reproducible drawing code.
license: MIT
metadata:
  version: "1.0.0"
---

# Research Figure Studio

Turn a verified scientific description into an editable figure, then improve it by inspecting rendered evidence. The three pillars are **semantic color**, **well-chosen reference figures**, and **screenshot-guided structural refinement**.

The bundled helpers require Python 3.10+ and Matplotlib. The agent needs local file access and a way to inspect rendered images.

Use the user's existing diagram, toolchain and publication requirements when supplied. The bundled Python library is a starting point, not a required replacement for an established SVG, PowerPoint, TikZ or diagram-editor workflow.

## Establish what the figure must say

Read the supplied method, code, equations and existing figure before drawing. Record the modules, representations, operations, dependencies and update states that the figure needs to communicate. Keep uncertain relationships explicit until verified; an attractive diagram is not evidence that a model works that way.

For multi-stage methods, distinguish forward computation, checkpoint reuse, parameter copying and optimization. A frozen component can still supply a representation. Detached gradients do not by themselves isolate a prediction path. Do not add experts, attention layers or training objectives merely to make a diagram look sophisticated.

Make useful progress with available information. Ask only for missing facts that affect the scientific meaning. If the user asks to **record feedback only**, write a compact pending-issue list and leave artwork and source unchanged.

## Choose references before polishing

For a new design, find a source figure with a comparable **computational structure**, and optionally another with a useful visual grammar. Inspect the actual figure, not only a text summary. If the user supplied references, start there.

Read [reference-reading.md](references/reference-reading.md) when selecting sources. Record the paper or official source, figure locator, what was actually inspected, which layout principle helps, and what must not be inherited. Borrow grouping, flow and typography rather than copying artwork or importing an unrelated mechanism.

If sources are unavailable, work from the verified graph and state that the reference has not been inspected. Keep unpublished inputs local unless the user has authorized sharing that material.

## Give color a job

Use categorical colors for module roles or methods, sequential scales for magnitude and diverging scales for signed deviations. Assign a stable meaning to each role across panels. Encode fixed/trainable, selected/unselected or forward/gradient state separately through labels, badges, line styles or symbols.

Read [palette.md](references/palette.md) for candidate colors and checks. The steel-blue / teal / warm-orange example is a configurable starting point, not a journal standard. Start with a light neutral background, dark text, and color concentrated on meaningful components. Strong contrast and hierarchy matter more than making every block dark or every panel tinted.

Check the final-size render in color and grayscale. Use a color-vision simulation when available, but do not call a simulation an accessibility certificate. Contrast thresholds are useful internal checks; actual journal requirements take precedence.

## Build an editable first version

For architecture diagrams, first make the graph and labels correct. Then fit groups, ports and routes to that graph. For charts, choose a form that supports the intended comparison before styling it.

- Use short module names and mathematical notation; move explanation into the caption or manuscript.
- Draw operator rings and symbols geometrically when typographic centering is unreliable.
- Group boxes need explicit inner padding. Their lower boundary must not coincide with contained boxes or the next component.
- Allocate more room to a dense junction region and less to long empty input-to-encoder gaps. Representation banks, side branches and inputs do not need to share a horizontal baseline.
- Route into actual boundary ports. Let a line leave a representation bar before turning; avoid drawing routes along its outline.
- Round only useful orthogonal bends. Protect endpoints and branch anchors before smoothing; crossings are not automatically junctions.

Use [scripts/figurekit.py](scripts/figurekit.py) when deterministic geometry, centered operators, contrast and editable SVG export would help. Inspect its API or a generated example before adapting it. Generate source code in the user's output workspace rather than editing an installed skill's own files.

## Refine against the rendered figure

Read [iteration-review.md](references/iteration-review.md) for the review loop. Each reported problem should identify a region, observable defect, intended reading and minimal correction. Distinguish scientific-logic corrections from geometry and palette adjustments.

An effective loop is:

1. Inspect the full figure and the cropped region at the intended display size.
2. Map feedback to actual module IDs, ports, frames or style tokens.
3. Change the smallest useful set of related elements. Move labels, badges and connected routes together.
4. Re-render the whole figure, not just the crop; inspect neighboring routes and group boundaries.
5. Verify the affected graph relationships, text fit, spacing and editable export.

Do not treat a fresh canvas as the default fix for a local defect. Do not keep optimizing indefinitely: finish when the requested defects are resolved and nearby content remains correct, or identify the remaining factual blocker.

Default to maintaining one adopted figure and its source. Preserve a historical version when requested, or follow an established project version policy. Do not delete unrelated assets while revising a figure.

## Preserve evidence in result charts

Compute transformations from original precision and round only visible labels. Keep paired comparisons, sign, zero reference and dataset/task grouping readable. Do not invent uncertainty, statistical significance, data or favorable axes. A model used as a reference is not automatically a theoretical upper bound.

When modifying an existing chart, verify that only the requested presentation changed unless the user supplied corrected data. A prettier figure must not silently alter the experimental claim.

## Deliver and verify

Deliver the adopted preview, editable vector file and reproducible drawing source, with the input data or concise checks needed to reproduce it. PNG + text-editable SVG is the default for the Python examples; other native editable formats are valid when they suit the user's workflow.

Open the rendered output. Check label overflow, unintended text overlap, arrow direction, group padding, symbol alignment, line joins and the final-size view. For Chinese or other non-Latin labels, select a locally available font with the necessary glyphs rather than assuming the example font covers them. Automated checks catch geometry and export errors; human inspection still decides readability and aesthetics. Verify that captions and manuscript links point to the adopted asset when updating a paper.

Use [case-study.md](references/case-study.md) to understand the real iteration lessons behind this workflow. Its generalized examples describe failure patterns, not additional scientific mechanisms or measured research results.
