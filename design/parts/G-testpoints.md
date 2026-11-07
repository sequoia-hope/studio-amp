# Test points and bring-up links (R-80)

Datasheet: datasheets/keystone-5015.pdf (Keystone 5015 SMD miniature test point, phosphor bronze,
tin plated).
Parts:
- `C2906768 5015 (Keystone, -): extended, JLC stock 52867, lifecycle normal, checked 2026-11-07`
  for loop test points on rails (clip-on).
- Second source `C5199798 RH-5015 (ronghe, -): extended, JLC stock 208968, lifecycle normal, checked 2026-11-07`.
- Bare 1.0 mm round pads (no part) for signals and scope-probe sites.

## Rules

- Every rail: one Keystone 5015 (clip-on) plus a GND 5015 within 15 mm. Rails with an isolation
  link get a pad on each side of the link.
- Every switch node: a bare pad on the SW copper with a **scope-probe ground-spring site** next to
  it: a GND pad 2.5–5 mm from the SW pad (size to the probe's tip-to-spring pitch; phase 4 fixes the
  pitch from the user's probes). SW pads are small, to keep SW copper area minimal.
- Signals: 1.0 mm bare pads, labelled on silk.

## List (blocks C and G; other blocks add their own)

| Net | Type | Note |
|---|---|---|
| VBUS | 5015 ×2 (both sides of the rails' input links) | 48 V. Silk "VBUS 48V" |
| GND | 5015 ×4 spread (power, logic, analog, I/O) | |
| +5V_BUCK, +5V, +5V_LED | 5015 | |
| VUSB | pad | |
| +3V3, +1V1, +2V5, +3V3_Q, +3V3_A | 5015 | 1V1 near the FPGA |
| VDRV | 5015 + pad at each LMG1210 after its link | |
| +18V_PRE, −17V4_PRE | pad | Fly-Buck primary/secondary before the ferrites |
| +15V, −15V | 5015 | at the LDO outputs, before the block F links |
| QWIIC_3V3 | pad | |
| SW_5V (LM5013) | pad + GND spring site | 0–56 V, 396 kHz |
| SW_VDRV (LM5017) | pad + GND spring site | 410 kHz |
| SW_AN (Fly-Buck LM5017) | pad + GND spring site | 498 kHz; also the secondary diode node, same treatment |
| SW_3V3, SW_1V1 (TPS62A02A) | pad + GND spring site | 2.4 MHz |
| PG_5V, PG_3V3, VDRV_EN, VDRV_PG | pad | sequencing |
| LED_EN, LED_FAULT_N, QWIIC_PWR_EN, QWIIC_FAULT_N | pad | |
| LED_DATA (5 V side), LED_CLK (5 V side) | pad | after the shifters |
| SDAB, SCLB (Qwiic side) | pad | shows the TCA9617B offset |
| PTP_PPS, 1-bit DAC stream | pad | owned by blocks E/F, listed here for completeness (R-80) |

## Isolation links (R-80)

The list is in `C-sequencing.md`, "Isolation links". Implementation:
- ≤ 1 A: KiCad `SolderJumper_2_Bridged` (copper-bridged, cut to open), 1 mm wide bridge.
- > 1 A (VBUS → 5 V buck, +5V_BUCK → LED switch): 0 Ω 1206 (rated per the maker's 0 Ω current,
  typically 2–5 A; phase 2 picks a part ≥ 3 A) or a 2 mm bridged jumper.

## Count

About 20 Keystone 5015 (both sides allowed, R-70) and about 25 bare pads for blocks C/G. Phase 4
places them on the probe-accessible side.
