# J (LED) — addressable LED output: TPS2553 current limit, SN74LV1T125 level shifters, JST PH (R-19)

Datasheets: datasheets/tps2553.pdf (SLVS841E), datasheets/sn74lv1t125.pdf (TI), datasheets/jst-ph-s4b.pdf
(JST PH catalogue; covers B4B-PH-K-S top entry and S4B-PH-K-S side entry), datasheets/murata-blm31pg.pdf
(BLM31 series incl. KN601), datasheets/mdd-smf5.0a.pdf, datasheets/pesd5v0s1bl.pdf.
Connector convention: R-19 (signed off) fixes a 4-pin JST PH in the order **5V, GND, D, C**. The only
addressable-LED output on Sequoia's boards (dancing_forest J5) is a Molex KK-254 3-pin
(1 +BATT, 2 DATA, 3 LEDGND), with TXS0101 shifters and no current limit. That isn't a match for a
data + clock strip, so R-19's PH 4-pin stands.

| Part | MPN | Supplier line |
|---|---|---|
| Current-limited switch (1.1 A) | TPS2553DRVR (WSON-6, 75 °C/W) | `C138719 TPS2553DRVR (TI, WSON-6-EP(2x2)): extended, JLC stock 26722, lifecycle normal, checked 2026-11-07` |
| Level shifter ×2 (data, clock) | SN74LV1T125DBVR | `C473338 SN74LV1T125DBVR (TI, SOT-23-5): extended, JLC stock 86549, lifecycle normal, checked 2026-11-07` |
| Connector, top entry | B4B-PH-K-S(LF)(SN) | `C131334 B4B-PH-K-S(LF)(SN) (JST, Through Hole,P=2mm): extended, JLC stock 141805, lifecycle normal, checked 2026-11-07` |
| (side-entry alternative) | S4B-PH-K-S(LF)(SN) | `C157926 S4B-PH-K-S(LF)(SN) (JST, Through Hole,Right Angle,P=2mm): extended, JLC stock 31067, lifecycle normal, checked 2026-11-07` |
| Ferrite on +5V_LED (R-90) | BLM31KN601SN1L | `C668306 BLM31KN601SN1L (muRata, 1206): extended, JLC stock 381, lifecycle normal, checked 2026-11-07` |
| TVS on +5V_LED | **SMF6.0A** (changed after review) | `C123790 SMF6.0A (MDD(Microdiode Semiconductor), SOD-123FL): extended, JLC stock 83315, lifecycle normal, checked 2026-11-07` |
| ESD on D, C | PESD5V0S1BL,315 ×2 | `C84374 PESD5V0S1BL,315 (Nexperia, DFN1006-2): extended, JLC stock 76124, lifecycle normal, checked 2026-11-07` |

## Circuit

`+5V_BUCK` → TPS2553 (IN 1 µF; EN = `LED_EN` RP2350 GPIO, 100 kΩ pull-down: off at boot;
FAULT_N → `LED_FAULT_N`, 10 kΩ to +3V3; RILIM 23.2 kΩ 1 %) → `+5V_LED` → 22 µF → BLM31KN601 →
SMF6.0A → J pin 1. J pin 2 GND.
`LED_DATA`, `LED_CLK` (RP2350 PIO, 3.3 V) → SN74LV1T125 A inputs. The shifters' VCC = `+5V_LED`
(before the ferrite), OE tied to GND, Y outputs → 47 Ω → PESD5V0S1BL → J pins 3 (D) and 4 (C).
For WS2812 single-wire strips, pin 4 is unused (the shifter can idle low).

Because both the strip and its drivers are powered from the switch, when `LED_EN` is low the strip
is unpowered and the shifters too, so nothing phantom-powers the first LED through its data pin. The
shifters' inputs tolerate 3.3 V with VCC = 0 (VI abs max 7 V independent of VCC). The LEDs are on
`+5V_BUCK`, so they are off on USB power by construction (R-23).

## Absolute max vs our worst case

| Parameter | Abs max | Ours | Margin |
|---|---|---|---|
| TPS2553 IN/OUT/EN/ILIM/FAULT | −0.3…7 V | 5.12 V | OK |
| TPS2553 IOUT (ROC) | 1.2 A (TJ ≤ 125 °C) / 1.5 A (≤ 105 °C) | 1.20 A max limit | OK |
| SN74LV1T125 VCC, VI | 7 V | 5.12 V; VI 3.3 V | OK |
| SN74LV1T125 VO, power-off / Hi-Z | 4.6 V | strip DIN/CIN don't drive back | OK (see gotcha) |
| SN74LV1T125 IO continuous | ±25 mA | 5 V / (47 Ω + strip) transient only | OK |
| JST PH contact | 2 A (AWG 24), 100 V | 1.2 A | 1.7× |
| BLM31KN601SN1L | 2.9 A rated (2.0 A derated), 0.045 Ω max | 1.2 A | OK |
| SMF6.0A VRWM (datasheets/mdd-smf5.0a.pdf, SMF series table) | 6.0 V; VBR 6.67–7.37 V; VC 10.3 V at 19.4 A | 5.12 V max | OK, below VRWM. VC exceeds the TPS2553's 7 V abs max only for the pulse; the ferrite sits between them |

## Calculations

**Current limit** (TPS2553 eq. 1): RILIM = 23.2 kΩ → IOS min 25230/23.2^1.016 = **1.034 A**, nom
23950/23.2^0.977 = **1.110 A**, max 22980/23.2^0.94 = **1.196 A**. That is above the 1 A firmware
ceiling at Class 8 (R-19: 5 W), so the hardware limit never cuts in during normal use, and below the
1.2 A ROC and the JST PH 2 A rating. Firmware limits by PoE class: 1.0 A (Class 8), 0.4 A
(Class 6, 2 W), 0 A (Type 2) (R-33a).

**Dissipation**: TPS2553DRV rDS(on) ≤ 150 mΩ (125 °C) → 1.2² × 0.15 = 0.22 W, θJA 75 °C/W (high-K)
→ +16 °C. Into a short it runs in constant current: (5.05 V × 1.1 A) = 5.5 W, which trips the thermal
sense and cycles. FAULT_N asserts after the 7.5 ms deglitch, and firmware turns `LED_EN` off.
Ferrite: 1.2² × 0.045 = 65 mW, 54 mV drop. The strip sees ≥ 4.9 V at 1 A.

**Level shifter**: at VCC 4.5–5.5 V, VIH(min) = 2.03–2.11 V, so 3.3 V CMOS from the RP2350 has 1.2 V
of margin. VOH ≥ 4.5 V at −8 mA (VCC 5 V) against WS2812/SK9822 VIH = 0.7 × VDD = 3.5 V. Data rate:
WS2812 800 kb/s; APA102/SK9822 clock usually ≤ 10–20 MHz. The LV1T125 is characterised to 50 MHz at
3.3 V VCC and faster at 5 V.

**Series resistor / ESD capacitance**: 47 Ω × (PESD5V0S1BL 35 pF typ + ≈ 50 pF/m cable) → τ ≈ 4 ns
at 1 m, an edge ≤ 10 ns. Fine for 20 MHz clock with a short cable. The 47 Ω also limits current into
the clamp: (5 V + 14 V clamp)/47 Ω peak only during ESD.

**Bulk on +5V_LED**: 22 µF X5R 10 V at the switch output. The strip has its own per-LED caps. The
TPS2553 soft start (rise 0.7–1.5 ms) limits inrush into them.

## Fine print / gotchas

- SN74LV1T125: "not recommended to float OE" (function table note). OE is tied to GND.
- SN74LV1T125: no Ioff spec in the datasheet, but VO in the power-off state is rated to 4.6 V max.
  With an externally powered strip and our `+5V_LED` off, the strip's DIN pin is an input, so nothing
  drives the shifter output. A strip whose power is back-fed into J pin 1 from its own supply is
  blocked by the TPS2553 reverse-voltage comparator (turns the switch off after 4 ms). The shifters
  then run from that external 5 V, which is harmless.
- TPS2553 has active-high EN (TPS2552 is active low). Don't substitute the 2552.
- TVS on +5V_LED is SMF6.0A (review): 5.12 V worst-case rail < 6.0 V VRWM. IR is specified ≤ 400 µA
  *at* 6.0 V (MDD p. 2), so the leakage at 5.12 V is lower, but not zero (≤ 2 mW worst case). The SMF5.0A stays on VUSB (≤ 5.25 V < its 6.4 V VBR min, G-usb-c.md).

## Layout guidance

- TVS and PESD diodes right at J, GND via each. Ferrite between the switch output cap and the TVS.
- RILIM short to the ILIM pin. The WSON-6 EP is GND with vias.

## Open questions

- **User: confirm the pin order 1 = 5V, 2 = GND, 3 = D, 4 = C** against the LED panel / cable in
  hand (R-19 order). Many SK9822/APA102 pigtails use a JST SM 4-pin with a different order, so an
  adapter cable may be needed.
- Top entry (B4B) or side entry (S4B): decide at phase 4 placement.

## Bring-up check (review note)
SN74LV1T125 has no Ioff figure. With `+5V_LED` off and LED_DATA/LED_CLK driven high, measure any
back-feed into `+5V_LED` at bring-up. If it is above ≈ 100 µA, have firmware hold both lines low
whenever `LED_EN` is low.

## Phase 2 (schematic, 2026-11-07)

TPS2553DRVR kept (θJA 75 °C/W). Symbol `studio_G:TPS2553DRV` from the DRV pin column (1 OUT,
2 ILIM, 3 FAULT, 4 EN, 5 GND, 6 IN, thermal pad = pad 7 on GND). Footprint: KiCad
`Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm`, checked against the DRV drawing (2.0 × 2.0 mm,
P 0.65, exposed pad 1.0 × 1.6 mm, datasheet pp. 31–32).
