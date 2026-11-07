# U (5V) — LM5013 5 V buck from VBUS, with inductor, diode and capacitors

Datasheet: datasheets/lm5013.pdf (SNVSCB3, Oct 2022). Read: all sections (features, pins, abs max,
ROC, EC, feature description 8.3.1–8.3.11, modes, application 9.2 incl. Type 3 ripple, layout).
MPN: LM5013DDAR   Supplier: `C5383001 LM5013DDAR (TI, PowerSOIC-8): extended, JLC stock 11098, lifecycle normal, checked 2026-11-07`
Second source: `C7589228 LM5013QDDARQ(TOKMAS) (Tokmas, ESOP-8-EP): extended, JLC stock 1334, lifecycle normal, checked 2026-11-07`. It is pin-compatible per its listing; read its own datasheet before substituting.
Footprint: SO-8 PowerPAD "DDA" (4.89 × 3.90 mm, 1.27 mm pitch, EP to GND). The mechanical drawing
is in the TI addendum. Phase 2 checks it against KiCad `Package_SO:TI_SO-PowerPAD-8_ThermalVias`.

Alternative considered: LMR38020SDDAR (C3192337, 9392 stock): synchronous, 2 A, 85 V abs max,
spread spectrum, syncable 300–2100 kHz (datasheets/lmr38020.pdf §7.1, §8.3.4). It is ≈ 0.4 W more
efficient at 1.5 A. It was rejected because 2 A is tight against 1.75 A at the hardware LED limit,
and 85 V is below the 100 V the GaN and the rest of the VBUS parts carry. Block B's VBUS TVS is an
SMCJ58A (VBR 64.4 V min, B-output.md), whose clamp voltage at pulse current is above 85 V, so the
LMR38020 is ruled out.

## Absolute max vs our worst case

| Parameter | Abs max (p.5) | Our worst case | Margin |
|---|---|---|---|
| VIN, EN/UVLO to GND | 100 V | 56 V static; TVS-clamped transients (block B) | OK, matches GaN 100 V |
| SW to GND | −1.5 V (−3 V < 20 ns) … 100 V | −VF(SS5P10) ≈ −0.7 V at 5 A | OK |
| BST to SW | 5.5 V | internal VCC 5 V | OK |
| FB, RON | 5.5 V | 1.2 V | OK |
| PGOOD | 14 V | 5.05 V pull-up | OK |
| CBST | 1.5–2.5 nF | 2.2 nF ±10 % X7R 50 V (DC bias negligible at 5 V) | OK (exact value required) |
| IOUT (ROC) | 3.5 A | 1.75 A (LED at hardware limit) | 2× |
| fSW (ROC) | ≤ 1000 kHz | 396 kHz | OK |
| tON (ROC) | 50–1000 ns | 226 ns (56 V) … 351 ns (36 V) | OK |
| TJ | 150 °C | 55 °C air + rise (est. < 30 °C) | OK |

## Required external parts (from datasheet)

- CBST 2.2 nF 50 V X7R BST–SW (pin table, p.4; abs max 1.5–2.5 nF). VCC has no current limit, so
  more capacitance can damage it (§8.3.2).
- Schottky DSW, mandatory (§8.3.8): VR ≥ 1.25 × VIN(max), current ≥ IPEAK.
- RRON on RON pin; RFB1/RFB2 on FB; EN/UVLO divider; PGOOD pull-up 10–100 kΩ to ≤ 14 V (§8.3.10).
- CIN ≥ 4.4 µF high-quality X7R/X7S, rated ≈ 2 × VIN (§9.2.2.6), close to VIN/GND.
- Ripple network: Type 3 (RA, CA, CB), because the output must be low-ripple for the LEDs and logic,
  and because COT needs ≥ 12 mV in-phase FB ripple (§8.3.1 note).
- EP to GND plane (no internal connection).

## Calculations

**Output voltage** (eq. 2, VREF 1.2 V, 1.181–1.218 V): RFB1 (top) = 100 kΩ (TI range 100 k–1 M),
RFB2 = 31.6 kΩ → 1.2 × (1 + 100/31.6) = 4.997 V. A Type 3 network adds ≈ ½ of the FB ripple as DC
(§9.2.2.7): 11.5 mV × 4.165 = +48 mV → **5.045 V nominal**, 4.97–5.12 V over the VREF spread. That
keeps +5V within the TPS62A02A (≤ 5.5 V) and TPS7A94 (≤ 5.7 V) after the mux. 1 % 0603 resistors.

**Switching frequency** (eq. 1/4): RRON = 31.6 kΩ → FSW = 5 × 2500 / 31.6 = **396 kHz**. This keeps
clear of the 768 kHz PWM's second harmonic and of the TPS62A02A logic bucks at 2.4 MHz. tON = RRON/(2.5·VIN)
gives 226 ns at 56 V and 351 ns at 36 V (> 50 ns). Below 300 ns on-time the minimum off-time is
forced to 250 ns (§8.3.7), so max duty at 56 V = 226/476 = 0.47. Duty needed is ≤ 5/36 = 0.14. OK.

**Inductor** (eq. 10, 11): design IOUT = 2.0 A (1.75 A at the LED hardware limit plus margin).
L = 22 µH (§9.2.2.3: ≥ 22 µH if transients can exceed 72 V; ours are TVS-bounded but unknown, so
22 µH is taken).
ΔIL = VOUT/(FSW·L)·(1 − VOUT/VIN) = 0.495 A (36 V) … 0.523 A (56 V), i.e. 26 % of 2 A.
IL(peak) = 2.0 + 0.26 = 2.26 A, below IPEAK min 3.7 A (EC, p.7), so current limit isn't hit in
normal operation.
Part: **SRP1265A-220M** (Bourns, datasheets/bourns-srp1265a.pdf): 22 µH ±20 %, DCR 32.5 typ /
37 mΩ max, Irms 9 A, Isat 12 A (−20 % L). TI recommends Isat > 7 A, and IPEAK max is 5 A, so OK.
Conduction loss 2.0² × 0.037 = 0.15 W. Operating temperature range −55…+125 °C per datasheet.
`C2041465 SRP1265A-220M (BOURNS, SMD,13.5x12.5mm): extended, JLC stock 6335, lifecycle normal, checked 2026-11-07`
Size is 13.5 × 12.5 × 6 mm. A smaller part with Isat ≥ 7 A at 22 µH is acceptable if phase 4 needs
the area.

**Schottky DSW**: VR ≥ 1.25 × 56 = 70 V → 100 V. IF(AV) ≥ IPEAK max 5 A (§9.2.2.4 "support the peak
current limit"). **SS5P10-M3/86A** (datasheets/vishay-ss5p10.pdf): 100 V, 5 A, VF 0.571 V at 2.5 A
/ 125 °C, IR 2.7 mA typ at 100 V / 125 °C, RθJA 65 °C/W on the recommended pad.
Loss = VF·IOUT·(1 − D) = 0.55 × 1.8 × 0.896 = **0.89 W** at full LED load (0.49 W at 1 A), so
ΔTJ ≈ 58 °C on the minimum pad. With R-40's 55 °C air that is ≈ 113 °C, under the 150 °C TJ max.
**Phase 4: give the TO-277A cathode tab ≥ 4 cm² of copper with vias.** Leakage loss at 56 V and
≈ 1 mA × 0.1 duty is negligible.
`C46986 SS5P10-M3/86A (VISHAY, TO-277A): extended, JLC stock 44365, lifecycle normal, checked 2026-11-07`

**Output capacitor** (eq. 13): COUT ≥ ΔIL/(8·FSW·ΔV) = 0.523/(8 × 396 k × 25 mV) = **6.6 µF
effective** (0.5 % ripple). Chosen: 3 × 22 µF 25 V X5R 1206 (CL31A226KAHNNNE, basic). DC-bias
derating at 5 V is assumed ≥ 50 % retained (Samsung's curve to be read at schematic time; MLCC rule
of thumb for a 25 V 1206). That gives ≥ 33 µF effective, about 5 mV ripple, and holds through a
1 A LED step (the COT responds within one cycle). Type 3 does not use COUT ESR, so the low ESR is fine.
`C12891 CL31A226KAHNNNE (Samsung Electro-Mechanics, 1206): basic, JLC stock 2037160, lifecycle normal, checked 2026-11-07`

**Input capacitor** (eq. 14/15, §9.2.2.6): 3 × 2.2 µF 100 V X7R 1210 (rated 2 × VIN) + 100 nF 100 V
0603 at the pins. At 48 V a 100 V X7R keeps roughly 50–60 % (to be checked on the maker's curve),
so ≥ 3.3 µF effective. Ripple = IOUT·D(1 − D)/(FSW·CIN) = 2 × 0.104 × 0.896 / (396 k × 3.3 µF)
= 0.14 V p-p. Acceptable; VBUS bulk is nearby.
Candidate: `C55151 CL32B225KCJSNNE` (Samsung, 1210, 100 V X7R, 30481 stock) or C153036 (PSA).

**Type 3 ripple network** (eq. 16–18):
- CA ≥ 10/(FSW·(RFB1‖RFB2)) = 10/(396 k × 24.0 k) = 1.05 nF → **CA = 3.3 nF** X7R.
- RA·CA ≤ (VIN − VOUT)·tON/20 mV = 565 µs at 48 V, 544 µs at 36 V → **RA = 150 kΩ** (495 µs).
- Resulting FB ripple = (VIN − VOUT)·tON/(RA·CA) = 22.0 mV (36 V), 22.9 mV (48 V), 23.3 mV (56 V).
  This is ≥ 12 mV at every input, as §9.2.2.7 requires.
- CB ≥ t_settle/(3·RFB1) = 75 µs / 300 kΩ = 250 pF → **CB = 330 pF C0G**.
- RA sees SW (0–56 V) and dissipates (VIN − VOUT)²·D/RA ≈ 1.2 mW. Use a 0603 rated 75 V.

**EN/UVLO** (eq. 5, 6): RUV1 (top) = 1.00 MΩ, RUV2 = 43.2 kΩ.
VIN(on) = 1.5 × (1 + 1000/43.2) = **36.2 V**, VIN(off) = 1.4 × 24.15 = **33.8 V**. Over the
thresholds' spread (1.43–1.6 V rising, 1.35–1.47 V falling) that is 34.5–38.6 V on and 32.6–35.5 V
off. That sits below VBUS min in service (48 V − 2 % − 10 % sag = 42.3 V), and above the point where
the logic would brown out uncontrolled. Hold-up from 48 V to 33.8 V on 5 mF at 8 W
(R-34) = ½ × 5 mF × (48² − 33.8²) / 8 W = **0.36 s** (≥ 20 ms; 73 ms even with only 1 mF).
RUV1 at 56 V: 3.1 mW. Use an 0805 (150 V working) for creepage and surge margin.

**PGOOD**: pulled up from `+5V_BUCK` (not from +3V3) through 56 kΩ, 100 kΩ to GND, giving
**PG_5V = 5.045 × 100/156 = 3.24 V** when good. It is 0 V whenever the buck is unpowered, so it
can't read "good" falsely when only USB powers the logic. Sink current 90 µA. Thresholds 95 % rise /
90 % fall of VREF (EC p.7), 5 µs deglitch. It drives TPS2116 PR1 (VREF 0.92–1.08 V) and an RP2350
or FPGA input (3.24 V < IOVDD + 0.3).

**Efficiency estimate at 1.8 A** (no 5 V curve in the datasheet; the curves are for 12 V out):
diode 0.89 W + HS conduction 1.8² × 0.25 Ω × 0.10 × 1.4 (hot) = 0.11 W + switching ≈ 0.5 W +
inductor 0.12 W + IQ 0.02 W ≈ 1.6 W for 9.1 W out, so **η ≈ 85 %**. Used in the budget in
`C-interfaces.md`.

## Fine print / gotchas

- The current-limit threshold is quoted as 3.2 A in §8.3.6 but as 3.7/4.2/5.0 A (min/typ/max) in
  the EC table, an inconsistency in the datasheet. Design to the table's 3.7 A minimum and size the
  inductor and diode for 5 A.
- CBST must be 1.5–2.5 nF. Never "upgrade" it to 0.1 µF.
- The internal soft start is fixed at 3.5 ms (1.75–4.75 ms). The mux sees PG_5V only after
  regulation.
- Light load enters sleep (10 µA IQ, 9 µs wake). Ripple at light load is set by PFM. The LED strip
  and logic always load > 50 mA, so this is a non-issue but should be measured at bring-up.
- The note after Fig. 9-1 says an electrolytic may be needed at the input for stability with a high
  source impedance. VBUS bulk (block B) is that capacitance; keep the buck within a few cm of it.

## Layout guidance from datasheet

- Keep CIN tight across VIN–GND (pins 2/1) and the hot loop CIN → VIN → SW → DSW → GND minimal.
  Put DSW's anode next to pin 1/EP ground.
- Keep the FB node small and RFB1/RFB2 at the FB pin, away from SW and the inductor. Route RA/CA
  from the SW node and COUT away from FB.
- EP to a large GND plane with vias (RθJC(bot) 1.3 °C/W).

## Open questions

- MLCC DC-bias curves for the chosen 22 µF/25 V and 2.2 µF/100 V parts (phase 2 picks the exact
  MPN and attaches the curve).
