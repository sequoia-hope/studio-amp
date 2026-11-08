"""hier.py -- hierarchical schematics on top of the skill's kicad_write.Schematic.

kicad_write writes one flat sheet. This adds what a multi-sheet project needs:

    SubSheet(name, ...)   a child sheet: symbol instance paths become
                          /<root uuid>/<sheet uuid>, power-symbol references get a
                          per-sheet number range (#PWR<base+n>) so they never collide
    write_root(...)       the root sheet: one sheet symbol per child, plus
                          free text and boxes drawn by the caller

The sheet list and every sheet's UUID live in SHEETS below, so each block's
generator can be run on its own and still land in the right place in the tree.
Inter-sheet signals use global labels (decisions.md, 2026-11-08); rails use
power symbols.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOARD_DIR = HERE.parent                       # hw/satellite/a
REPO = BOARD_DIR.parents[2]
sys.path.insert(0, str(REPO / ".claude/skills/pcb-design/scripts"))

from kicad_write import GRID, S, Schematic, Sym, SymbolLib, dump, new_uuid, yes  # noqa: E402
from kicad_files import child, children, head  # noqa: E402

PROJECT = "satellite"
ROOT_UUID = "5a7e1117-0000-4000-8000-000000000000"

# name, file, title, page, reference range base, block owner.
# UUIDs are fixed so that regenerating one sheet never re-annotates another.
SHEETS = [
    # name          title                                   page  base  block
    ("poe_in",      "PoE++ input: magjack, bridges, PD",      2,  100, "A"),
    ("iso_dcdc",    "Isolated active-clamp forward, 48 V",    3,  200, "B"),
    ("iso_aux",     "Converter sync clock and VBUS droop",    4,  250, "B"),
    ("rails",       "Secondary rails and sequencing",         5,  300, "C"),
    ("amp_woofer",  "GaN BTL power stage: woofer",            6,  400, "D"),
    ("amp_tweeter", "GaN BTL power stage: tweeter",           7,  500, "D"),
    ("amp_sense",   "VBUS, current and temperature sensing",  8,  600, "D"),
    ("mcu",         "RP2350B, flash, USB",                    9,  700, "E"),
    ("fpga",        "ECP5 FPGA and configuration",           10,  800, "E"),
    ("ethernet",    "Ethernet PHY and clocks",               11,  900, "E"),
    ("audio_out",   "1-bit DAC, headphone and line out",     12, 1000, "F"),
    ("audio_in",    "Measurement mic and MEMS mic",          13, 1100, "F"),
    ("io",          "User I/O, debug and test points",       14, 1200, "G"),
]
SHEET_UUID = {name: f"5a7e1117-{page:04d}-4000-8000-{page:012d}" for name, _, page, _, _ in SHEETS}


def project_libs() -> SymbolLib:
    """System libraries plus every project symbol library in lib/."""
    return SymbolLib(extra=sorted((BOARD_DIR / "lib").glob("*.kicad_sym")))


class SubSheet(Schematic):
    def __init__(self, name: str, rev: str = "A", date: str = "2026-11-08", paper: str = "A3",
                 libs: SymbolLib | None = None, comments: list[str] | None = None):
        row = next(r for r in SHEETS if r[0] == name)
        _, title, page, base, block = row
        super().__init__(PROJECT, title=f"Studio Amp satellite: {title}", rev=rev, date=date,
                         company="Sequoia Alexander, github.com/sequoia-hope/studio-amp",
                         comments=comments or [f"Block {block}. Audits: design/parts/{block}-*.md"],
                         paper=paper, libs=libs or project_libs())
        self.name, self.page, self.base = name, page, base
        self.uuid = SHEET_UUID[name]          # the child file's own uuid
        self._pwr = base * 10                 # #PWR references: 1000-1999 for base 100, ...

    @property
    def file(self) -> Path:
        return BOARD_DIR / f"{self.name}.kicad_sch"

    def save(self, path: Path | None = None):
        path = Path(path or self.file)
        inst = f"/{ROOT_UUID}/{SHEET_UUID[self.name]}"
        for it in self.items:
            if head(it) != "symbol":
                continue
            for pr in children(child(it, "instances"), "project"):
                p = child(pr, "path")
                p[1] = inst
        super().save(path)
        # A child file carries no sheet_instances block of its own.
        import re
        text = re.sub(r"\n\t\(sheet_instances\n(?:\t\t.*\n)*\t\)", "", path.read_text())
        text = re.sub(r"\n\t\(sheet_instances[^\n]*\)", "", text)
        path.write_text(text)

def write_root(layout: dict[str, tuple[float, float, float, float]], notes=(), boxes=()):
    """layout: sheet name -> (x, y, w, h) of its sheet symbol on the root page."""
    sch = Schematic(PROJECT, title="Studio Amp satellite, variant A", rev="A", date="2026-11-08",
                    company="Sequoia Alexander, github.com/sequoia-hope/studio-amp",
                    comments=["PoE++ GaN speaker amplifier. Design: design/intent.md, design/architecture.md",
                              "Open source, MIT. Sheets in block-diagram order: power in -> amp -> compute -> audio"],
                    paper="A3")
    sch.uuid = ROOT_UUID
    for name, title, page, _, block in SHEETS:
        x, y, w, h = layout[name]
        eff = lambda j: [Sym("effects"), S("font", S("size", GRID, GRID)), [Sym("justify"), *[Sym(t) for t in j.split()]]]
        sch.items.append([
            Sym("sheet"), S("at", x, y), S("size", w, h), S("exclude_from_sim", yes(False)),
            S("in_bom", yes(True)), S("on_board", yes(True)), S("dnp", yes(False)),
            S("fields_autoplaced", yes(True)),
            S("stroke", S("width", 0.1524), S("type", Sym("solid"))),
            S("fill", S("color", 0, 0, 0, 0.0)), S("uuid", SHEET_UUID[name]),
            S("property", "Sheetname", name, S("at", x, y - 0.7116, 0), eff("left bottom")),
            S("property", "Sheetfile", f"{name}.kicad_sch", S("at", x, y + h + 0.5884, 0), eff("left top")),
            S("instances", S("project", PROJECT, S("path", f"/{ROOT_UUID}", S("page", str(page))))),
        ])
        sch.text(f"{title}\n(block {block})", (x + 1.27, y + 2.54))
    for a, b, label in boxes:
        sch.box(a, b, label)
    for s, at in notes:
        sch.text(s, at)
    sch.save(BOARD_DIR / f"{PROJECT}.kicad_sch")
    return sch
