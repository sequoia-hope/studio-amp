"""Root sheet: one sheet symbol per block, laid out like design/architecture.md's block diagram.
Run: python3 hw/satellite/a/gen/root.py"""
import hier

W, H = 62, 30
L = {  # name: (x, y, w, h), A3 landscape: power entry left -> amp right; compute row; audio and I/O
    "poe_in":     (20, 50, W, H), "iso_dcdc":    (100, 50, W, H), "rails":     (180, 50, W, H),
    "amp_woofer": (260, 50, W, H), "iso_aux":    (100, 95, W, H), "amp_sense": (180, 95, W, H),
    "amp_tweeter": (260, 95, W, H),
    "ethernet":   (20, 160, W, H), "fpga":       (100, 160, W, H), "mcu":       (180, 160, W, H),
    "audio_out":  (260, 160, W, H), "io":        (180, 210, W, H), "audio_in":  (260, 210, W, H),
}
notes = [
    ("PoE (primary side, isolated 1500 Vrms) -> isolated forward converter -> VBUS 48 V -> rails and GaN bridges",
     (20, 30)),
    ("Compute: LAN8720A RMII <-> ECP5 (PWM, MAC, PTP, 1-bit DAC) <-> PIO 8-bit link <-> RP2350B", (20, 150)),
    ("Inter-sheet signals are global labels; rails are power symbols. Net names: design/parts/*-interfaces.md",
     (20, 255)),
]
if __name__ == "__main__":
    hier.write_root(L, notes=notes, boxes=[((15, 36), (335, 132), "POWER AND AMPLIFIER"),
                                           ((15, 140), (335, 262), "COMPUTE, NETWORK, AUDIO AND I/O")])
