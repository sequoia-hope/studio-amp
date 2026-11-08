# U (5V) — LM5013 5 V buck from VBUS, with inductor, diode and capacitors

## Revision 3 (3rd review, 2026-11-07): UVLO lowered for the PoE-loss hold-up; RRON trimmed

- **EN/UVLO: RUV2 43.2 kΩ → 52.3 kΩ** (RUV1 1.00 MΩ): on = 1.5 × (1 + 1000/52.3) = **30.2 V** (28.8–32.2 V),
  off = 1.4 × 20.12 = **28.2 V** (27.2–29.6 V). That is below the 34.6 V VBUS reaches 20 ms after block B's
  40 V PoE-loss comparator trips at 60 W on 6 mF (C-sequencing.md). Start-up is unchanged in practice
  (VBUS ≥ 43 V in service).
- **RRON 69.8 kΩ → 64.9 kΩ**, so tON stays inside the 1000 ns ROC down to the lowest UVLO-off:
  tON = 64.9/(2.5·VIN) µs + 30 ns = **984 ns at 27.2 V**, 347 ns at 82 V. Real frequency ≈ **212–214 kHz**
  over 30–82 V. Beat rule (a, b ≤ 2 vs 576 / 737.28 kHz, ±15 % spread): worst clearance **84 kHz**,
  ≥ 40 kHz. The 3rd-harmonic residual is as recorded in C-interfaces.md (now crossing 576 kHz at the
  low end of the band).
- ΔIL at 214 kHz = 0.45 A, still in CCM above 0.23 A. Type 3 RA·CA limit at 36 V = 31 × 0.75 µs/20 mV =
  1.16 ms ≥ 1.09 ms (RA 330 kΩ, CA 3.3 nF), ripple ≈ 21 mV. Unchanged parts otherwise.

Datasheet: datasheets/lm5013.pdf (SNVSCB3, Oct 2022). Read: all sections (features, pins, abs max,
ROC, EC, feature description 8.3.1–8.3.11, modes, application 9.2 incl. Type 3 ripple, layout).
MPN: LM5013DDAR   Supplier: `C5383001 LM5013DDAR (TI, PowerSOIC-8): extended, JLC stock 11098, lifecycle normal, checked 2026-11-07`
Clone (not a second source): `C7589228 LM5013QDDARQ(TOKMAS) (Tokmas, ESOP-8-EP): extended, JLC stock 1334, lifecycle normal, checked 2026-11-07`. A third-party copy whose RON constant, current limit and CBST window aren't guaranteed to match TI's. **Not a drop-in until its own datasheet is audited.**
Footprint: SO-8 PowerPAD "DDA" (4.89 × 3.90 mm, 1.27 mm pitch, EP to GND). The mechanical drawing
is in the TI addendum. Phase 2 checks it against KiCad `Package_SO:TI_SO-PowerPAD-8_ThermalVias`.

Alternative considered: LMR38020SDDAR (C3192337, 9392 stock): synchronous, 2 A, 85 V abs max,
spread spectrum, syncable 300–2100 kHz (datasheets/lmr38020.pdf §7.1, §8.3.4). It is ≈ 0.4 W more
efficient at 1.5 A. It was rejected because 2 A is tight against 1.75 A at the hardware LED limit,
and 85 V is below the 100 V the GaN and the rest of the VBUS parts carry. Block B's VBUS TVS is an
SMCJ51A/SMBJ51A (51 V stand-off, 82.4 V clamp; agreed after block B's review). 82.4 V plus
overshoot exceeds 85 V, so the LMR38020 is ruled out.


## Revision 2 (2026-11-07, team lead's beat rule): fsw ≈ 200 kHz, supersedes the 690 kHz design in Revision 1

**Rule (logged in C-interfaces.md; see there for the 2nd-review correction on harmonics):** every |a·f_buck − b·f| with a, b ≤ 2, against f = 576 kHz
(amp PWM) and 737.28 kHz (ACF, crystal-locked), stays ≥ 40 kHz across the buck's real frequency
spread. The ACF clock-fail fallback band doesn't count, because the amp is muted then.

**Frequency.** A sweep of 165–1000 kHz (the LM5013's tON ≤ 1000 ns sets the floor) favours the low
end. Real f_c = **≈ 200 kHz**: worst clearance **116 kHz at ±15 %** spread (136 kHz at ±10 %); the
limiting product is |2·230 − 576|.
- **RRON = 69.8 kΩ.** tON = 69.8/(2.5·VIN) µs + ≈ 30 ns (LM5013 p. 7 tON3–tON6 measured points; 2nd review
  m-4): **≈ 886 ns at 32.6 V** (the UVLO-off corner; ≤ 1000 ns ROC, 11 % margin; the corner exists only
  during the UVLO-off ramp), 801 ns at the 36.2 V turn-on,
  776 ns at 36 V, 582 ns at 48 V, **499 ns at 56 V, 340 ns at the 82.4 V clamp** (≥ 50 ns). tON > 300 ns,
  so the minimum off-time is 50 ns and duty isn't limited.
- Real f = D/tON with D = (5.05 + 0.55)/(VIN + 0.55): 197 kHz (36 V), 198 kHz (48 V), 199 kHz (56 V),
  199 kHz (82 V). The diode drop rises with load, so the frequency rises a few %. The ±15 % band
  (170–230 kHz) covers that plus the unspecified tON tolerance. At very light load (DCM) the frequency
  falls, which only moves products further from 576/737 kHz. The 47 µH inductor keeps CCM above
  0.24 A, and the logic alone draws more than that.
- **Inductor → SRP1265A-470M** (Bourns, same 13.5 × 12.5 mm body): 47 µH ±20 %, DCR 76 typ / 90 mΩ max,
  Irms 6.5 A, Isat 9.5 A (> the 7 A TI recommends and the 5 A IPEAK max).
  `C840530 SRP1265A-470M (BOURNS, SMD,13.5x12.5mm): extended, JLC stock 1561, lifecycle normal, checked 2026-11-07`
  Alternative: MDA1365-470M (KOHER, C2847587, 2507; verify Isat). ΔIL = 5/(200 k × 47 µ) × (1 − 5/56) =
  0.48 A (0.50 A at 82 V); Ipk at 2.0 A = 2.25 A, against IPEAK min 3.7 A. Loss 1.8² × 0.09 = 0.29 W.
- **COUT** ≥ 0.48/(8 × 200 k × 25 mV) = 12 µF effective. 3 × 22 µF 25 V 1206 (≥ 33 µF effective) gives
  ≈ 9 mV ripple. Unchanged parts.
- **Type 3**: CA ≥ 10/(200 k × 24.0 k) = 2.1 nF → **CA 3.3 nF**. RA·CA ≤ (VIN − VOUT)·tON/20 mV =
  1.20 ms (36 V), 1.27 ms (56 V), 1.31 ms (82 V) → **RA = 330 kΩ 0805** (1.09 ms). FB ripple 22.1 mV
  (36 V), 23.3 mV (56 V), ≥ 12 mV. DC offset ≈ +47 mV, so VOUT ≈ 5.04 V (unchanged). CB 330 pF C0G
  (≥ 250 pF).
- **CIN**: 2 × 4.7 µF 100 V 1210 (≥ 4.4 µF effective, kept). Input ripple
  IOUT·D(1 − D)/(f·CIN) = 2 × 0.104 × 0.896/(200 k × 4.7 µ) = 0.20 V p-p at the converter. Input RMS
  current 2 × √(0.104 × 0.896) = 0.61 A, shared by two 1210s and the VBUS bulk.
- **Efficiency at 1.8 A**: diode 0.89 W + switching 0.5 × 48 × 1.8 × 15 ns × 2 × 200 kHz = 0.26 W +
  inductor 0.29 W + HS conduction 0.11 W + IQ 0.02 W = 1.57 W for 9.1 W out → **η ≈ 85 %** (back from
  82 % at 690 kHz).
- **VBUS ripple at f_buck (product amplitude)**: the input current is a 2 A, D ≈ 0.10 pulse train.
  Its fundamental is (2 × 2 A/π)·sin(π × 0.104) = 0.41 A peak. The VBUS bulk (≈ 6 mF, 5–7 cans in
  parallel, ESR ≈ 5 mΩ combined + ESL, block B) takes most of it: ≈ 0.41 A × ≈ 6 mΩ ≈ **2.5 mV peak at
  200 kHz** on 48 V, i.e. −86 dB (5 × 10⁻⁵ relative). Open-loop PWM turns VBUS ripple into output
  AM, so the mix products with the 576 kHz carrier sit at ≥ 116 kHz (by the rule above). That is out
  of band, and the output LC filter attenuates them further, ≈ −30 dB more at 116 kHz for a
  tens-of-kHz corner (block D's filter). The in-band product amplitude is zero by construction. Even
  a hypothetical in-band product at full 1 W signal would be 2.83 Vrms × 5 × 10⁻⁵ = 0.15 mVrms before
  the −30 dB LC filter, i.e. ≈ 5 µVrms, ≪ R-51's 150 µV noise. Second-order products are a further
  −86 dB down.

## Revision 1 after phase 1 review (2026-11-07): the frequency items here are superseded by Revision 2; the CIN and PGOOD items still apply

**Switching frequency moved to ≈ 690 kHz.** 396 kHz nominal (≈ 440 kHz real, because the COT on-time
is set from VOUT but the duty includes the diode drop) sat on block B's ACF (400 kHz ±6 % →
376–424 kHz, 2nd harmonic 752–848 kHz) and block D's 448 kHz (896, 1344 kHz), and their beat
products could land in the audio band.
- RRON = **20.0 kΩ** → tON = 20/(2.5·VIN) µs = 222 ns (36 V), 167 ns (48 V), 143 ns (56 V), all
  ≥ 50 ns. The forced 250 ns off-time applies (tON < 300 ns): max duty 143/393 = 0.36 ≥ 0.15 needed.
- Real frequency with the diode: f = D/tON, D = (5.05 + 0.55)/(VIN + 0.55) → 690 kHz (36 V),
  692 kHz (48 V), 693 kHz (56 V); lower in DCM at light load.
- Distances to the nearest products, up to the 4th harmonic: 2×ACF band 752 kHz (−60 kHz);
  3×ACF ≥ 1128 kHz vs 1384 kHz; 448 → 1344 vs 1384 (40 kHz); 512 (block E fallback) → 1536 vs 1384,
  2048 vs 2076 (28 kHz). All above 20 kHz.
- **Block B's ACF is moving from 400 kHz** (currently 620 kHz, to be settled with D/E): 690 vs 620 kHz
  is 70 kHz apart, and 2×/3× products are ≥ 140 kHz apart. **Re-check RRON when block B reports
  the final frequency.**
- **If block D moves to 672 kHz**, 690 kHz is only 18 kHz away: retune RRON then (e.g. 22.1 kΩ →
  ≈ 625 kHz).
- Inductor ripple drops: ΔIL = 5/(690 k × 22 µ) × (1 − 5/56) = 0.30 A; Ipk 2.15 A.
- COUT ≥ 0.30/(8 × 690 k × 25 mV) = 2.2 µF. The 3 × 22 µF keeps a large margin.
- Type 3: CA ≥ 10/(690 k × 24.0 k) = 0.60 nF → **CA 3.3 nF** (kept). RA·CA ≤ (VIN − VOUT)·tON/20 mV
  = 344 µs (36 V), 364 µs (56 V) → **RA = 100 kΩ** (330 µs). FB ripple = 20.9 mV (36 V) … 22.1 mV
  (56 V), ≥ 12 mV ✓. DC offset ≈ 11 mV × 4.165 = +45 mV, so VOUT ≈ 5.04 V (unchanged).
  CB ≥ 250 pF → 330 pF C0G (kept).
- Cost: switching loss ≈ 0.5 × 48 V × 1.8 A × 15 ns × 2 × 690 kHz = 0.89 W, against 0.51 W at
  396 kHz. **η ≈ 82 % at 1.8 A** (≈ 84 % at 1 A), +0.4 W at full load. This is accepted for the audio
  band; it is included in the C-interfaces budget.

**CIN raised to the datasheet's ≥ 4.4 µF effective** (§9.2.2.6): 2 × 4.7 µF 100 V X7R 1210
(FS32X475K101EGG) + 100 nF 100 V 0603. At 48 V assume ≥ 50 % retained → ≥ 4.7 µF (attach the PSA
DC-bias curve in phase 2).
`C381466 FS32X475K101EGG (PSA, 1210): extended, JLC stock 41237, lifecycle normal, checked 2026-11-07`

**PGOOD / PG_5V, review B2.** The PGOOD divider (56 kΩ / 100 kΩ from +5V_BUCK, Thevenin 36 kΩ) stays,
**but it now drives only TPS2116 PR1** (input leakage ≤ 0.1 µA). LM5013 asks for a 10–100 kΩ pull-up
(pin table), so the reviewer's 5.62 k/10 k option was out of range. The FPGA must not load this node:
the ECP5's unconfigured GPIO pulls down 30–150 µA, which would drag PR1 under its 0.92–1.08 V
reference and deadlock the start-up. The FPGA gets a **buffered, inverted copy**: a 2N7002 (gate on
PG_5V, gate current ≈ 0) drains a 4.7 kΩ pull-up to +3V3 → `PG_5V_N` → FPGA B3 (**active low = good**).
Before configuration B3's pull-down acts only on the 4.7 kΩ node: with PG low (FET off) it gives
3.3 − 4.7 k × 150 µA = 2.6 V (≥ VIH 2.0 V); with PG high (FET on) it reads ≈ 0 V. 2N7002 Vth
1.0–2.5 V at 250 µA, VGS = 3.24 V, so it is on; the drain current is 0.7 mA.
`C8545 2N7002 (JSCJ, SOT-23): basic, JLC stock 5965543, lifecycle normal, checked 2026-11-07`

**+5V minimum at block F's relay coils (≥ 4.76 V requested, coils need ≥ 4.75 V), checked 2026-11-07.**
FB divider resistors are now **0.5 %** (100 kΩ / 31.6 kΩ).
- Buck minimum: VREF 1.181 V (EC min) × (1 + 100·0.995/(31.6·1.005)) = 4.881 V, plus the Type 3 DC
  offset (≥ 20.9 mV ripple / 2 × 4.13 = +43 mV) → **≥ 4.92 V**.
- Path drops at the 0.91 A +5V design load: buck-to-mux trace (also carrying LED current, 1.75 A ×
  ≤ 10 mΩ, phase 4 rule) ≤ 18 mV; TPS2116 RON ≤ 60 mΩ (−40…105 °C, p. 5) × 0.91 A = 55 mV; +5V
  distribution to the relays (56 mA, ≤ 0.1 Ω) ≤ 6 mV; AO3400A ≤ 1.5 mV (block F).
- **Worst-case coil voltage ≥ 4.84 V**, 80 mV above the 4.76 V requirement.
- Load steps on +5V_BUCK (1 A LED step) cause short COT undershoot (tens of µs, not quantified in
  the datasheet). It doesn't affect relay hold. Pick-up is ms-scale.
- On USB-only power the relays are off (block F), so VUSB's 4.75 V minimum doesn't apply.
- Maximum: 1.218 × (1 + 100·1.005/(31.6·0.995)) + 0.05 = 5.20 V, within every +5V and +5V_BUCK
  load (TPS62A02A 5.5 V, TPS7A94 5.7 V, TPS2116 5.5 V, LEDs).

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
Conduction loss 2.0² × 0.037 = 0.15 W. Operating temperature range −55…+150 °C per datasheet (reviewer-confirmed).
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
- RA sees SW (0–56 V, up to ≈ 91 V during a TVS-clamped surge) and dissipates ≈ 1–2 mW. **Use 0805
  (150 V working)**: a 0603's 75 V is below the clamp.

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

## Open: frequency plan after block B moved to 737.28 kHz (2026-11-07), decision needed

Requirement (team lead / block B): every |a·f_buck − b·g| for a, b ≤ 3 is > 100 kHz, where
g ∈ {576 kHz amp, 737.28 kHz ACF crystal-locked, 590–708 kHz ACF fallback}, across the buck's own
tolerance.

Result of a numerical sweep over f = 150–1200 kHz (scratch script; COT frequency tolerance ±10 %
and ±15 % for line, load and part spread):
- **No free-running frequency meets it.** The 118 kHz fallback band × 2 and × 3 covers every
  window. Even counting only the two fixed tones, the best clearance is 81 kHz (at 150 kHz, ±10 %)
  and ≈ 45 kHz near 985 kHz.
- **The LM5013 also has its own floor**: the ROC limits tON ≤ 1000 ns, so at the 33.8 V UVLO-off
  RRON ≤ 84.5 kΩ, giving f_real ≥ ≈ 165 kHz. The only clear region (f ≤ 144 kHz, where 3·f stays
  below 576 − 100 kHz) is therefore out of reach.
- Today's 690 kHz is 47 kHz from 737.28 kHz and inside the 590–708 kHz fallback band, so it fails.

**Recommended fix: lock the 5 V buck to the system clock grid.** 576 kHz = 25 × 23.04 kHz and
737.28 kHz = 32 × 23.04 kHz. A buck synchronised to n × 23.04 kHz from the FPGA puts every
intermodulation product on an exact multiple of 23.04 kHz, never in the audio band, whatever a and
b are. In the crystal-fallback case the ACF itself is off-grid, so its products with *any*
converter are unavoidable; that is a fault mode.
- Candidate: **LM5146-Q1** (TI, 100 V synchronous buck *controller* with SYNCIN; LM5146QRGYRQ1,
  C1850329, 2455 in stock). It needs two external 100 V N-FETs and a new full audit. The datasheet
  has not been read yet.
- Rejected: LM5148 (80 V, below the 82.4 V clamp), LMR38020/38025 (85 V; 38025 has no stock),
  LT8631 (10 in stock), LM5165 (0.15 A).
- Proposed sync frequency: 460.8 kHz (20 × 23.04) or 368.64 kHz (16 × 23.04), both ≥ 115 kHz from
  576 and 737.28 kHz. Needs one FPGA output (block E). Before the FPGA configures, the buck runs
  free at its RT frequency; the amp is muted then. On USB-only power there is no VBUS.
- Interim, if the redesign is declined: keep the LM5013 and pick the least-bad free-running point.
  From the sweep that is ≈ 985 kHz real (RRON ≈ 14 kΩ, tON ≈ 69 ns at 82 V, near the 50 ns floor, and still only ≈ 45 kHz clearance) or
  ≈ 150–165 kHz (blocked by tON max). **Neither is acceptable, which is why the sync redesign is
  recommended.**

VBUS TVS in this file: SMCJ51A at the bulk / SMBJ51A at the bridges, VBR 56.7–62.7 V, clamp 82.4 V
(confirmed; see C-interfaces.md).
