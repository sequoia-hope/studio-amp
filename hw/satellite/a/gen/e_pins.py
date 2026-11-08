"""e_pins.py -- block E pin data shared by lib_E.py, fpga.py and mcu.py.

Sources (nothing here is typed from memory):
  design/datasheets/lattice-ECP5U-25-pinout.csv   Lattice pinout, column CABGA256
  design/parts/E-pinmap.md                        block E's authoritative net per ball / pin

ecp5_balls()  ball -> {"func", "bank", "dual", "diff"} for all 256 CABGA256 balls
fpga_nets()   ball -> (net, dir, block, note)   from the E-pinmap.md FPGA table
rp_nets()     QFN-80 pin -> (name, net, dir, note) from the E-pinmap.md RP2350B table
FPGA_DECOR    the passives at each FPGA ball (series R, pulls), checked against the notes
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CSV = REPO / "design/datasheets/lattice-ECP5U-25-pinout.csv"
PINMAP = REPO / "design/parts/E-pinmap.md"
ROWS = "ABCDEFGHJKLMNPRT"


def ecp5_balls() -> dict[str, dict]:
    rows = [r for r in csv.reader(CSV.open()) if r and r[0] and not r[0].startswith("#")]
    hdr = rows[0]
    ci = hdr.index("CABGA256")
    out = {}
    for r in rows[1:]:
        b = r[ci].strip()
        if b in ("-", ""):
            continue
        if b in out:
            raise ValueError(f"ball {b} twice in the CSV")
        out[b] = {"func": r[1], "bank": r[2], "dual": "" if r[3] == "-" else r[3],
                  "diff": "" if r[4] == "-" else r[4]}
    want = {f"{R}{c}" for R in ROWS for c in range(1, 17)}
    if set(out) != want:
        raise ValueError(f"CSV CABGA256 balls != 16x16 grid: {sorted(set(out) ^ want)}")
    return out


def _md_rows():
    for line in PINMAP.read_text().splitlines():
        if line.startswith("| ") and "`" in line:
            yield [c.strip() for c in line.strip().strip("|").split("|")]


def fpga_nets() -> dict[str, tuple[str, str, str, str]]:
    balls = ecp5_balls()
    out = {}
    for c in _md_rows():
        if len(c) >= 7 and re.fullmatch(r"[A-T]\d{1,2}", c[0]) and c[0] in balls and c[3].startswith("`"):
            net = c[3].strip("`")
            if c[0] in out:
                raise ValueError(f"E-pinmap.md: ball {c[0]} twice")
            out[c[0]] = (net, c[4], c[5], c[6])
    return out


def rp_nets() -> dict[str, tuple[str, str, str, str]]:
    out = {}
    for c in _md_rows():
        if len(c) >= 5 and re.fullmatch(r"\d{1,2}", c[0]):
            out[c[0]] = (c[1], c[2].strip("`").split("`")[0], c[3], c[4])
    return out


def partner(ball: str, balls=None) -> str | None:
    balls = balls or ecp5_balls()
    d = balls[ball]["diff"]
    if "_OF_" not in d:
        return None
    name = d.split("_OF_")[1]
    return next((b for b, r in balls.items() if r["func"] == name), None)


# Passives drawn at the FPGA (fpga sheet). E-fpga-ecp5-passives.md; checked below against the
# E-pinmap.md notes. ser = series R between the ball and the outside net; pu/pd = pull to
# +3V3 / GND at the ball (pu_far: on the outside net, beyond the series R); gnd = tied to GND.
FPGA_DECOR: dict[str, dict] = {
    # bank 0, always-powered status inputs
    "PD_PG_N": {"ser": "1k"}, "PD_TPH_N": {"ser": "1k"}, "PD_TPL_N": {"ser": "1k"}, "PD_BT_N": {"ser": "1k"},
    "POE_LOSS_N": {"ser": "1k", "pu_far": "4k7"}, "ACF_PULSE": {"ser": "4k7"},
    "PG_5V_N": {"ser": "1k"}, "PG_3V3_N": {"ser": "1k"}, "PG_3V3Q": {"ser": "1k"},
    # bank 2/3/7, always-driven inputs on the hot-socket pairs
    "HP_FAULT_N": {"ser": "1k"}, "HP_DET": {"ser": "1k"}, "LED_FAULT_N": {"ser": "1k"},
    "QWIIC_FAULT_N": {"ser": "1k"}, "VUSB_DET": {"ser": "1k"}, "DC_W_n": {"ser": "1k"}, "DC_T_n": {"ser": "1k"},
    "FAULT_W_n": {"ser": "330R"}, "FAULT_T_n": {"ser": "330R"},
    "MADC_DOUT": {"ser": "330R"}, "PDM_DAT": {"ser": "330R"},
    # ADC chip selects held high through configuration
    "VB_CS_n": {"pu": "4k7"}, "IS_CS_n": {"pu": "4k7"}, "PF_CS_n": {"pu": "4k7"},
    # sysCONFIG (TN-02038 Tab 6.2, TN-02039 Tab 4.5) and JTAG (Tab 6.1)
    "FPGA_CCLK": {"pu": "1k"}, "FPGA_SN": {"pu": "4k7"}, "FPGA_HOLDN": {"pu": "4k7", "local": True},
    "FPGA_PROGRAMN": {"pu": "4k7"}, "FPGA_INITN": {"pu": "4k7"}, "FPGA_DONE": {"pu": "4k7"},
    "FPGA_CFG0": {"pu": "4k7", "local": True}, "FPGA_CFG1": {"gnd": True, "local": True},
    "FPGA_CFG2": {"gnd": True, "local": True},
    "FPGA_TDI": {"pu": "4k7"}, "FPGA_TMS": {"pu": "4k7"}, "FPGA_TDO": {"pu": "4k7"}, "FPGA_TCK": {"pd": "4k7"},
}


def check_decor():
    """Every series R / pull named in an E-pinmap.md note is in FPGA_DECOR and vice versa,
    except the PHY-side parts, which are drawn on the ethernet sheet."""
    errs = []
    phy_side = {"RMII_TXEN", "RMII_RXD0", "RMII_RXD1", "RMII_CRSDV", "PHY_MDIO", "PHY_NRST", "PHY_NINT"}
    # pulls fitted by the block at the far end (C, F, G), and CCLK's 33 Ω at the RP2350 (mcu sheet)
    elsewhere = {"DISP_BL_PWM", "LED_EN", "QWIIC_PWR_EN", "LED_FAULT_N", "HP_EN", "LO_EN", "FPGA_CCLK"}
    for ball, (net, _d, _b, note) in fpga_nets().items():
        m = re.search(r"(\d+) (k?)Ω series", note)
        ser = (m.group(1) + ("k" if m.group(2) else "R")) if m else None
        if ser == "4.7k":
            ser = "4k7"
        dec = FPGA_DECOR.get(net, {})
        if net in ("PG_5V_N", "PG_3V3_N"):    # 1 kΩ per E-fpga-ecp5-passives.md (15 slow inputs)
            ser = "1k"
        if net == "ACF_PULSE":
            ser = "4k7"
        if net == "FPGA_CCLK":
            ser = None
        if (dec.get("ser") or None) != ser:
            errs.append(f"{ball} {net}: note says series {ser}, FPGA_DECOR {dec.get('ser')}")
        pulled = re.search(r"pull-(up|down)", note)
        if pulled and net not in phy_side | elsewhere and not (dec.get("pu") or dec.get("pd") or dec.get("pu_far")):
            if "at D" not in note and "block" not in note.split("pull")[0][-30:]:
                errs.append(f"{ball} {net}: note mentions a pull, FPGA_DECOR has none")
        partner_nc = re.search(r"partner (\w+) NC", note)
        if partner_nc and partner(ball) != partner_nc.group(1):
            errs.append(f"{ball}: partner is {partner(ball)}, note says {partner_nc.group(1)}")
    nets = {v[0] for v in fpga_nets().values()}
    errs += [f"FPGA_DECOR {n}: not in E-pinmap.md" for n in FPGA_DECOR if n not in nets]
    return errs


if __name__ == "__main__":
    b = ecp5_balls()
    f = fpga_nets()
    r = rp_nets()
    print(len(b), "balls;", len(f), "FPGA balls assigned;", len(r), "RP2350 pins")
    for e in check_decor():
        print("CHECK", e)
