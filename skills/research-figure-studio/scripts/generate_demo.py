"""Generate original fictional examples, not figures or results from a real paper.

Run from any directory: python path/to/generate_demo.py --output-dir output/
Only the output directory is written; no remote service or AI account is required.
"""
import argparse
import json
from pathlib import Path

from figurekit import Figure, PALETTE, contrast


def architecture(out):
    f = Figure(1040, 570, inches=11.6)
    f.label(520, 31, "A model diagram should explain the computation", 15, True)
    f.panel(24, 76, 425, 438, "1 / Preparation")
    f.panel(538, 76, 475, 438, "2 / Task adaptation")
    # A fictional shared-feature architecture, used only to demonstrate drawing.
    for x, label in [(70, "Head A"), (265, "Head B")]:
        f.box(x, 136, 130, 44, label, "teal")
    f.box(170, 225, 130, 46, r"Gate $g(x)$", "teal", shape="gate")
    f.box(170, 315, 130, 40, r"Features $h$", "blue", fill=PALETTE["representation"])
    f.box(155, 405, 160, 46, "Encoder", "blue", dark=True)
    f.label(235, 482, "Input features", 10)
    f.route([(235, 470), (235, 451)])
    f.route([(235, 405), (235, 355)], "blue")
    f.route([(235, 315), (235, 271)], "blue")
    f.route([(200, 225), (200, 204), (135, 204), (135, 180)], "teal")
    f.route([(270, 225), (270, 204), (330, 204), (330, 180)], "teal")
    f.box(555, 405, 160, 46, "Frozen encoder", "blue", dark=True)
    f.box(570, 315, 130, 40, r"Features $h$", "blue", fill=PALETTE["representation"])
    f.box(825, 315, 150, 40, "Adapter", "orange", dark=True)
    f.box(695, 225, 130, 46, r"Gate $g_j(x)$", "teal", shape="gate")
    f.box(695, 136, 130, 44, "New-task head", "teal")
    f.label(635, 482, "Input features", 10)
    f.route([(635, 470), (635, 451)])
    f.route([(635, 405), (635, 355)], "blue")
    f.route([(700, 335), (825, 335)], "orange")
    f.route([(635, 315), (635, 248), (701, 248)], "blue")
    f.route([(900, 315), (900, 248), (819, 248)], "orange")
    f.route([(760, 225), (760, 180)], "teal")
    # Reuse is a parameter relationship, not another forward-pass input.
    f.route([(315, 428), (555, 428)], "line", "copy")
    f.label(435, 409, "checkpoint reuse", 8.8)
    for x, y, label in [(708, 402, "F"), (965, 312, r"$\Delta$"),
                         (817, 222, r"$\Delta$"), (817, 133, r"$\Delta$")]:
        f.box(x-9, y-10, 18, 20, label, size=8, fill=PALETTE["canvas"])
    f.label(520, 541, "Blue: shared features     Teal: task prediction     Orange: adaptation     F: fixed     Δ: update", 9)
    report = f.export(out / "editable-architecture")
    f.close()
    return report


def mini(f, x, phase):
    """Same hypothetical graph, three illustrative layout states."""
    y = 112
    names = ["01 / Initial draft", "02 / References + palette", "03 / Screenshot refinement"]
    f.panel(x, 67, 465, 423, names[phase])
    f.label(x+232.5, 105, ["Hierarchy is unclear", "Structure is visible; spacing is tight", "Ports, symbols and padding are checked"][phase], 9)
    if phase == 0:
        f.box(x+105, y+263, 245, 42, "Input feature representation encoder", size=8.3,
              fill="#C8EDF2", border="#6D9DAD")
        f.box(x+125, y+145, 205, 40, "Intermediate representation", size=8.3,
              fill="#D7D0F0", border="#8A78B0")
        f.box(x+140, y+21, 175, 42, "Task-specific prediction head", size=8.0,
              fill="#F5D7C5", border="#BF8C68")
        f.route([(x+227, y+263), (x+227, y+185)], radius=0)
        f.route([(x+227, y+145), (x+227, y+63)], radius=0)
        f.label(x+232, 454, "Long labels · large gaps · little semantic coding", 8.2)
        return
    # Expose prompt conditioning that the draft hid inside its prediction block.
    # This relationship belongs to the fictional method, not to its visual references.
    enc_y, rep_y = (382, 303) if phase == 1 else (359, 279)
    prompt_y, op_y = (225, 239) if phase == 1 else (213, 233)
    f.box(x+128, enc_y, 170, 42, "Encoder", "blue", dark=True)
    f.box(x+138, rep_y, 150, 36, r"Features $h$", "blue", fill=PALETTE["representation"])
    f.box(x+112, 145, 180, 42, "Prediction head", "teal")
    f.box(x+310, prompt_y, 95, 40, r"Prompt $e_j$", "teal", size=8.4)
    f.operator(x+213, op_y, radius=11)
    f.route([(x+213, enc_y), (x+213, rep_y+36)], "blue")
    f.route([(x+213, rep_y), (x+213, op_y+11)], "blue")
    f.route([(x+213, op_y-11), (x+213, 187)], "teal")
    if phase == 1:
        f.route([(x+310, prompt_y+20), (x+280, prompt_y+20), (x+280, op_y), (x+224, op_y)], "teal", radius=0)
        # Explicitly depict the unfinished padding, without changing the graph.
        f.box(x+95, 132, 325, prompt_y+40-132, fill="none", border=PALETTE["border"]).set_zorder(0)
    else:
        f.route([(x+310, op_y), (x+224, op_y)], "teal")
        f.box(x+95, 132, 325, 137, fill="none", border=PALETTE["border"]).set_zorder(0)
    f.label(x+213, enc_y+61, "Input", 8.5)
    f.route([(x+213, enc_y+51), (x+213, enc_y+42)], "line")
    f.label(x+232, 454, ["", "Compare the crop, then fix the local defect", "Aligned input · centred glyph · clear margins"][phase], 8.2)


def board(out):
    f = Figure(1510, 535, inches=16)
    f.label(755, 28, "From 0 to 1: three complementary improvements", 16, True)
    for phase, x in enumerate([25, 523, 1021]):
        mini(f, x, phase)
    f.label(755, 515, "Illustrative teaching examples; these are not historical figures or experimental results from a paper.", 9)
    report = f.export(out / "iteration-board", strict=False)
    f.close()
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir.resolve(); out.mkdir(parents=True, exist_ok=True)
    reports = {"architecture": architecture(out), "iteration_board": board(out)}
    reports["palette_contrast"] = {key: round(contrast("#FFFFFF", PALETTE[key]), 3)
                                   for key in ("blue", "teal", "orange")}
    reports["provenance"] = "Original fictional demonstration. No manuscript, private code, or experiment data is used."
    reports["board_note"] = "The initial/intermediate panels intentionally illustrate shortcomings; final architecture passes geometry QA."
    (out / "demo-audit.json").write_text(json.dumps(reports, indent=2), encoding="utf8")
    print(json.dumps({"output": str(out), "architecture_QA": reports["architecture"]}, ensure_ascii=True))


if __name__ == "__main__":
    main()
