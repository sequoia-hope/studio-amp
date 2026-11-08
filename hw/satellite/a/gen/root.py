"""Root sheet: one sheet symbol per block, drawn as the block diagram of design/architecture.md.
Inter-sheet signals are global labels, so the lines here are graphics that show the main flows.
Run: python3 hw/satellite/a/gen/root.py"""
import hier

W, H = 62, 30
L = {  # name: (x, y, w, h), A3 landscape
    "poe_in":     (20, 50, W, H), "iso_dcdc":   (100, 50, W, H), "rails":     (180, 50, W, H),
    "amp_woofer": (262, 50, W, H), "iso_aux":   (100, 98, W, H), "amp_sense": (180, 98, W, H),
    "amp_tweeter": (262, 98, W, H),
    "ethernet":   (20, 160, W, H), "fpga":      (100, 160, W, H), "mcu":       (180, 160, W, H),
    "audio_out":  (262, 160, W, H), "io":       (180, 210, W, H), "audio_in":  (262, 210, W, H),
}
# (points, label, label position): arrows point the way power or the main signal flows
FLOWS = [
    ([(82, 62), (100, 62)], "VPRI 42-57 V", (83, 60)),
    ([(100, 70), (82, 70)], "UCC_SS", (84, 73.5)),
    ([(162, 62), (180, 62)], "VBUS 48 V", (163, 60)),
    ([(242, 58), (262, 58)], "VBUS, VDRV 7 V", (243, 56)),
    ([(242, 70), (252, 70), (252, 108), (262, 108)], "VBUS, VDRV", (243, 73.5)),
    ([(131, 80), (131, 98)], "ACF_SYNC, DRV_FWD", (133, 90)),
    ([(262, 118), (242, 118)], "I, V, T sense", (244, 121.5)),
    ([(30, 80), (30, 160)], "ETH pairs, LEDs", (32, 120)),
    ([(82, 172), (100, 172)], "RMII + 50 MHz", (83, 170)),
    ([(162, 172), (180, 172)], "PIO link, SSPI config", (163, 170)),
    ([(150, 160), (150, 146), (292, 146), (292, 128)], "PWM, FAULT, ARM (both bridges)", (190, 144)),
    ([(118, 128), (118, 160)], "POE_LOSS_N, ACF_PULSE", (88, 145)),
    ([(131, 190), (131, 200), (282, 200), (282, 190)], "1-bit DAC, MCLK_Q, relays", (190, 198)),
    ([(262, 222), (252, 222), (252, 206), (140, 206), (140, 190)], "I2S mic ADC, PDM", (160, 209.5)),
    ([(205, 190), (205, 210)], "USB, SWD, I2C, LED, display", (207, 203)),
    ([(70, 80), (70, 142), (108, 142), (108, 160)], "PD status (ISO7740)", (72, 140)),
]
NOTES = [
    ("PoE (primary side, isolated 1500 Vrms) -> isolated forward converter -> VBUS 48 V -> rails and GaN bridges",
     (20, 34)),
    ("Inter-sheet signals are global labels and rails are power symbols; the lines on this page show the main flows.",
     (20, 250)),
    ("Net names: design/parts/*-interfaces.md and E-pinmap.md", (20, 254)),
    ("COMPUTE, NETWORK, AUDIO AND I/O", (190, 155.5)),
]
if __name__ == "__main__":
    hier.write_root(L, notes=NOTES, flows=FLOWS,
                    boxes=[((15, 40), (335, 138), "POWER AND AMPLIFIER"),
                           ((15, 152), (335, 244), None)])
