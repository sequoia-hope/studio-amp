# J (USB) — USB-C receptacle, CC pull-downs, ESD (R-23, R-42)

Datasheets: datasheets/hro-type-c-31-m-12.pdf (HRO drawing, 1 page, dimensioned, no text layer),
datasheets/usblc6-2sc6.pdf (ST), datasheets/mdd-smf5.0a.pdf (MDD).
Connector convention (Sequoia's boards): HRO TYPE-C-31-M-12 on round-pendant (`power.kicad_sch`),
servodrive and comms; the XKB U262-16XN-4BVC11 on the rp2350 boards. ESD: USBLC6-2P6/-2SC6 with two
separate 5.1 kΩ CC resistors. This board follows the newer HRO convention.

| Part | MPN | Supplier line |
|---|---|---|
| Receptacle 16-pin USB 2.0, SMD + 4 shell legs | TYPE-C-31-M-12 | `C165948 TYPE-C-31-M-12 (Korean Hroparts Elec, SMD): extended, JLC stock 320343, lifecycle normal, checked 2026-11-07` |
| D+/D− ESD + VBUS clamp | USBLC6-2SC6 (ST) | `C7519 USBLC6-2SC6 (ST, SOT-23-6L): extended, JLC stock 25409, lifecycle normal, checked 2026-11-07` |
| VBUS TVS | SMF5.0A (SOD-123FL) | `C193402 SMF5.0A (MDD(Microdiode Semiconductor), SOD-123FL): extended, JLC stock 472221, lifecycle normal, checked 2026-11-07` |
| CC1, CC2 pull-downs | 5.1 kΩ 1 % 0402 ×2 (basic) | phase 2 |

Footprint: KiCad `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12` (as on servodrive/comms). It is
through-hole for the shell legs, so check the PTH drill sizes against the HRO drawing in phase 2.

## Circuit

- A6/B6 (D+) tied together, A7/B7 (D−) tied together, then through the USBLC6-2SC6 to the RP2350
  USB pins. Pins (Figure 1): 1–6 = I/O1 flow-through (D+), 3–4 = I/O2 flow-through (D−), 2 GND,
  5 VBUS → VUSB. The 27 Ω series resistors are block E's, per
  the RP2350 hardware design.
- CC1 and CC2: one 5.1 kΩ to GND each (Rd, UFP sink). They must be separate resistors, never shared,
  or a cable could short CC1 to CC2. Not routed to an ADC (no spare ADC channels; see open question).
- VBUS pins A4/B4/A9/B9 → `VUSB` → SMF5.0A to GND at the connector → 4.7 µF → TPS2116 VIN2
  (C-5v-mux.md). Keep ≤ 10 µF on VUSB (USB attach inrush limit).
- `VUSB_DET` (ECP5 pin E14, 3.3 V bank, VIH 2.0 V): VUSB → 15.0 kΩ → node → 22.0 kΩ → GND, so 5.25 V × 22/37 =
  3.12 V max (≤ VCCIO 3.3 V), 4.75 V → 2.82 V (LVCMOS33 VIH 2.0 V). 0 V when unplugged.
  Load 0.14 mA. Add 100 nF on the node against ESD and cable noise.
- Shell: to GND directly through the 4 legs, the usual practice for a bring-up port. The secondary
  GND is user-touchable anyway (R-10/R-32). Add a footprint for an optional 1 MΩ ‖ 4.7 nF to GND
  (shell isolated) in case EMC testing wants it.
- SBU1/SBU2 not connected.

## Calculations / checks

- ESD part capacitance vs signal speed: USB 2.0 FS 12 Mb/s (edge 4–20 ns). USBLC6 Ci/o-GND
  3.5 pF max, Ci/o-i/o 1.7 pF max at 1.65 V. Negligible at FS (it is also rated for HS 480 Mb/s).
- USBLC6 VRM 5.25 V leakage 150 nA max. Clamp 12 V at 1 A, 17 V at 5 A (8/20 µs). IEC 61000-4-2
  level 4 (±8 kV contact, ±15 kV air), which meets R-42.
- SMF5.0A: VRWM 5.0 V, VBR 6.4–7.0 V at 10 mA, IR ≤ 400 µA at 5 V, VC 9.2 V at IPP 21.7 A (8/20 µs),
  200 W peak pulse. Max USB 2.0 VBUS 5.25 V is below VBR min 6.4 V, so it never conducts in normal use.
  Leakage at 5.25 V ≤ 400 µA (worst case) is a negligible load. The TPS2116's 6 V abs max is
  exceeded only during the ESD event's nanoseconds (accepted, see C-5v-mux.md).
- CC: Rd = 5.1 kΩ ±10 % per the Type-C sink requirement. 1 % used.
- Current: the board draws ≤ 0.55 A from USB (≤ 0.33 A with Qwiic power off). The contacts are rated
  for far more. Firmware keeps the draw under 500 mA by keeping Qwiic off on USB power.

## Fine print / gotchas

- USBLC6 layout (datasheet §"ESD protection: layout"): ≈ 6 nH of track per path adds ≈ L·di/dt to
  the clamp. Keep the VBUS-pin, I/O and GND traces of the USBLC6 as short as possible, and put it right
  at the connector with GND vias at its pin 2.
- USBLC6 VBUS pin must connect to VUSB (not +5V), so it can't back-bias from the board side.

## Open questions

- CC current-advertisement sensing (Default/1.5 A/3 A) would let USB-only mode run Qwiic loads. It
  costs 2 ADC inputs, which the RP2350B doesn't have spare (block E). Proposed: not fitted in variant A.

## Review note (2026-11-07): unconfigured current
The board draws ≈ 0.3 A from VUSB before USB enumeration (USB 2.0 allows 100 mA until configured).
That is normal for a bring-up port, but some hosts may warn. Recorded against R-23; firmware can't
change it because the logic needs that much to run. `VUSB_DET` to ECP5 E14: during the ≈ 2 ms
between VUSB appearing and +3V3 rising, the 15 kΩ limits injection into the unpowered bank to
≤ 0.2 mA (ECP5 DS Table 3.5: IDK_HS ≤ ±1 mA on top/bottom banks; left/right banks need the current
limited, which 15 kΩ does). Before configuration its 30–150 µA pull-down reads the node at
1.8–3.1 V. That is informational only and controls no power.
