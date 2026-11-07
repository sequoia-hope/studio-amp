# Block C — secondary rails: topology, budget, interfaces

Phase 1 audit summary for block C (sheet `rails`). Per-part audits:
`C-5v-buck.md`, `C-5v-mux.md`, `C-3v3-1v1-bucks.md`, `C-2v5-ldo.md`, `C-3v3a-ldo.md`, `C-3v3q-ldo.md`, `C-vdrv-buck.md`,
`C-pm15-flybuck.md`, `C-pm15-ldos.md`, `C-sequencing.md`. All datasheets are in
`design/datasheets/` and listed in `design/datasheets/sources-CG.csv`. Checked 2026-11-07.

## Rail tree

```
VBUS 48 V (43–56 V working; 100 V parts throughout)
 ├─ U  LM5013 (100 V, 3.5 A non-sync COT)  → +5V_BUCK 5.05 V, ≤ 2.0 A design
 │     ├─ TPS2553 (1.1 A limit)           → +5V_LED  → JST PH LED connector   (off on USB)
 │     └─ TPS2116 power mux, VIN1 priority → +5V  (logic 5 V)
 │            VIN2 ← VUSB (USB-C)            ├─ TPS62A02AP (FPWM) → +3V3 (0.79 A design, 1 A peak, ±2.4 %)
 │                                           │     ├─ (PG_3V3 →) TPS7A9401 → +2V5 (ECP5 VCCAUX, 50 mA)
 │                                           │     └─ PG_3V3 → EN of 1V1 buck and 2V5 LDO
 │                                           ├─ TPS62A02AP (FPWM) → +1V1 = 1.101 V (ECP5 VCC, 400 mA, < 1 mV ripple)
 │                                           ├─ TPS7A2033P → +3V3_A (block D sense reference, 15 mA, always on)
│                                           └─ (relay coils, block F, 56 mA; block D 25 mA)
 ├─ U  LM5017 (100 V, 600 mA sync COT)     → VDRV 7.0 V, 200 mA design (LMG1210 VIN ×4)
 │     enabled only by VDRV_EN (firmware); TLV6703 → VDRV_PG
 └─ U  LM5017 Fly-Buck, 1:1 coupled L      → +18V4_PRE / −17V8_PRE
           ├─ TPS7A4901 → +15V (120 mA design, 62 mA avg)
           │     ├─ TPS7A4901 → +5V_A (≤ 15 mA, ADC analog / mic bias)
           │     └─ EN_UV of TPS7A9401 → +3V3_Q (35 mA, 0.46 µVrms; from +5V)
           └─ TPS7A3001 → −15V (110 mA design, 50 mA avg)
```

Every converter fed from VBUS is rated 100 V (LM5013, LM5017; their caps and diodes 100 V),
the same rating as the GaN FETs, so they survive anything the VBUS TVS lets through (block B).

## Part list (block C)

| Function | MPN | LCSC | Stock 2026-11-07 | Lib |
|---|---|---|---|---|
| 5 V buck | LM5013DDAR (TI); 2nd source LM5013QDDARQ(TOKMAS) | C5383001 / C7589228 | 11098 / 1334 | ext |
| 5 V buck inductor 22 µH | SRP1265A-220M (Bourns) | C2041465 | 6335 | ext |
| 5 V buck diode 100 V 5 A | SS5P10-M3/86A (Vishay); alt SS5P10-M3(TOKMAS) C52941004 | C46986 | 44365 | ext |
| 5 V power mux | TPS2116DRLR | C3235557 | 53288 | ext |
| 3V3 and 1V1 bucks (forced PWM) | TPS62A02APDDCR ×2 | C25687169 | 2304 | ext |
| 3V3/1V1 inductor 1.0 µH | SRP4020TA-1R0M (Bourns); 2nd MDA4020-1R0M (KOHER) | C913245 / C2847468 | 5040 / 1077 | ext |
| +2V5 LDO (ECP5 VCCAUX) | TPS7A9401DSCR (2nd instance) | C5220127 | 2441 | ext |
| 3V3_Q LDO (input +5V, enabled by +15V) | TPS7A9401DSCR | C5220127 | 2441 | ext |
| 3V3_A LDO (block D reference) | TPS7A2033PDBVR | C2862740 | 129111 | ext |
| VDRV buck | LM5017MRX/NOPB | C34355 | 12815 | ext |
| VDRV inductor 47 µH | SRN6045TA-470M (Bourns) | C5151734 | 4173 | ext |
| VDRV power-good | TLV6703DDCT | C2877614 | 538 | ext |
| ±15 V Fly-Buck | LM5017MRX/NOPB (second instance) | C34355 | 12815 | ext |
| Fly-Buck coupled inductor 47 µH 1:1 | PSSCAQ7048M-470M (PROD Tech); 2nd SRF0703-470M (Bourns) | C56266203 / C3273458 | 996 / 204 | ext |
| Fly-Buck secondary diode | B1100-13-F (Diodes) | C110106 | 29855 | ext |
| +15 V and +5V_A LDOs | TPS7A4901DGNR ×2 | C16430 | 5633 | ext |
| −15 V LDO | TPS7A3001DGNR | C33835 | 5267 | ext |

Build quantity 5 boards: every line above has ≥ 40× the need except SRF0703-470M (second source
only) and TLV6703 (538, need 5).

## The ±15 V decision (R-33a)

**Chosen: an LM5017 Fly-Buck (isolated-buck topology, used non-isolated) from VBUS, 1:1 coupled
inductor, primary regulated at +18.0 V, secondary rectified to ≈ −17.4 V, then TPS7A4901 /
TPS7A3001 low-noise LDOs to ±15 V.** Assumes no aux winding on the forward transformer (block B).

Why:
- One controller and one 7.6 mm coupled inductor make both polarities. The secondary tracks the
  regulated primary (AN-2292 eq. 2: VOUT2 = N2/N1·VOUT1 − VF), so the negative rail needs no second
  loop. Its looser regulation (leakage, diode drop) is absorbed by the LDO headroom (≥ 2.3 V).
- Fed from VBUS, so the analog load stays off the 5 V buck and the USB path, and the rails are off
  on USB-only power (R-23) without extra switching.
- 100 V part, rated like the GaN. LM5017 is in stock (12815). The same IC is reused for VDRV, which
  cuts the BOM by one part type.
- The LDOs are 15–20 µVrms, 72 dB PSRR at 120 Hz, and above 55 dB from 10 Hz to 700 kHz
  (TPS7A30 datasheet, "Maximum AC performance"), which covers the ≈ 500 kHz Fly-Buck ripple.

Alternatives rejected:
- **Buck + separate inverting buck-boost from VBUS**: the inverter's switch sees VIN + |VOUT|
  ≈ 74 V. That needs a second 100 V converter and inductor, and it doesn't make the board simpler.
- **From +5V (SN6505B push-pull + transformer, or TPS65131-class boost/inverter)**: this puts
  ≈ 3.3 W (0.7 A) more on the 5 V buck and the mux, and needs a transformer (SN6505B: 1288 stock).
  TPS65131-class parts reach only ±15 V before post-regulation, so there is no LDO headroom.
- **Isolated DC-DC module (±15 V 3 W)**: its switching frequency and noise are unknown, it is a
  single source, and it costs more.
- **Capacitance multipliers instead of LDOs**: they give no regulation against Fly-Buck
  cross-regulation drift, so they are kept only as a block F option.

## Power budget (recomputed from these parts; average, worst case)

| Rail | Load | Converter efficiency (est.) | From its source |
|---|---|---|---|
| +3V3 | design 0.79 A (block E 350 mA + Qwiic 300 + display 40 + block D 45 + 2V5 LDO 50) = 2.61 W; typ 0.32 A with Qwiic unloaded | TPS62A02A ≈ 90 % | 2.9 W (typ 1.17 W) from +5V |
| +2V5 | 50 mA (from +3V3, inside the +3V3 line) | LDO | — |
| +1V1 | design 0.40 A × 1.10 V = 0.44 W; typ ≈ 0.25 A (block E estimate) | FPWM ≈ 82 % | 0.54 W (typ 0.34 W) from +5V |
| +3V3_Q | 0.035 A | LDO from 5 V | 0.18 W from +5V |
| +3V3_A (block D sense reference) | 0.015 A | TPS7A2033P from 5 V | 0.08 W from +5V |
| block D direct | +3V3 45 mA (comparators, logic), +5V 25 mA (optional ADS8353) | — | 0.29 W from +5V |
| relay coils (block F) | 56 mA × 5 V | — | 0.28 W from +5V |
| +5V (mux out) | total | mux 40 mΩ | **4.3 W, 0.86 A design** (2.0 W typ), incl. block D and 3V3_A |
| +5V_LED | 1.0 A firmware limit at Class 8 (hardware 1.03–1.20 A) | TPS2553 + ferrite ≈ 97 % | 5.15 W |
| +5V_BUCK | 1.55 A (1.75 A at the hardware LED limit) | LM5013 ≈ 85 % (diode-dominated) | **9.3 W from VBUS at Class 8**; 5.7 W at Class 6 (2 W LEDs) |
| VDRV | 42 mA at 480 kHz, 79 mA at 1 MHz (IGB070S10S1, block D) | LM5017 ≈ 80 % at light load | 0.37–0.65 W from VBUS |
| ±15 V (+5V_A inside +15V) | avg 62 + 50 mA → 1.68 W + 0.35 W LDO loss (design 120/110 mA: 4.2 W) | Fly-Buck ≈ 85 % | **2.4 W avg** from VBUS (4.9 W at design load) |

Against R-33a at Class 8 (it assumes logic 2.9 W, gate drive 1.0 W, analog 2.8 W, LEDs 5.8 W;
12.5 W total), revised 2026-11-07 after blocks D, E (ECP5) and F:
- **Worst case** (block E design loads incl. 1V1 400 mA and 2V5 50 mA, Qwiic loaded to 300 mA,
  LEDs 1 A, block D loads incl. the optional ADS8353, relays, 1 MHz): +5V 4.3 W + LEDs 5.15 W →
  9.45/0.85 = 11.1 W vs 8.7 W (**+2.4 W**, of which ≈ 1 W is the Qwiic load R-33a didn't list,
  ≈ 0.45 W block D's sensing, and ≈ 0.4 W the ECP5's higher core/aux power); gate drive 0.65 W
  (**−0.35 W**); analog 2.4 W average (**−0.4 W**). **Net ≈ +1.65 W**, ≈ 1.5 W off the speaker
  average at 90 %.
- **Typical** (block E typ, 1V1 ≈ 0.25 A per block E, Qwiic idle, 480 kHz): (2.05 + 5.15)/0.85 =
  8.5 W (−0.2 W); gate 0.37 W (−0.63 W); analog −0.4 W. **Net ≈ −1.2 W.**
- Analog is budgeted at block F's averages (62/50 mA); the 120/110 mA design figures are short-term
  only.

## Interfaces this block offers (net names per architecture.md, plus new ones)

| Net | To | Spec |
|---|---|---|
| `+5V_BUCK` (new) | LED switch, mux VIN1 | 5.05 V ±1.5 %, ≤ 2.0 A |
| `+5V` | 3V3 and 1V1 bucks, 3V3_Q and 3V3_A LDOs, relays, block D | 5.05 V (buck) or VUSB (4.75–5.25 V), 0.86 A design, mux limit 2.5 A |
| `+3V3` | RP2350, ECP5 VCCIO (all banks, max 3.465 V), PHY, Qwiic switch, display, block D, +2V5 LDO | 3.318 V ±2.4 % (0.5 % divider), 0.79 A design, ≤ 1 A peak |
| `+1V1` | ECP5 VCC (no bead) | 1.101 V, 1.075–1.128 V worst case (spec 1.045–1.155 V incl. noise), 0.5 mV p-p ripple, 400 mA design |
| `+2V5` (new) | ECP5 VCCAUX (block E adds a 120 Ω bead + 10 µF) | 2.505 V ±1 %, 50 mA, 0.46 µVrms, ≈ 2 mV/µs ramp, up on USB power |
| `+3V3_A` (new) | block D INA241 ×4, OCP thresholds, ADS7042/ADS7038 AVDD | 3.30 V ±1.5 %, ≤ 15 mA, 7 µVrms, always on with +5V |
| `+3V3_Q` | block F reclock FFs | 3.30 V ±1.1 %, 35 mA design, 0.46 µVrms; PG_3V3Q → block E; **present only while +15V ≥ 7 V** (block F request); FFs need Ioff inputs |
| `VDRV` | LMG1210 VIN ×4 (block D) | 7.04 V ±2 %, ≤ 200 mA; drivers' own LDO makes VDD |
| `+15V` / `-15V` | block F | 14.94 V / −15.09 V; 120 / 110 mA continuous design, 200 / 190 mA fault (LDO 150 / 200 mA ratings; the + side current-limits in the fault) |
| `+5V_A` (new) | block F ADC analog, mic bias | 5.04 V, ≤ 15 mA, 15 µVrms, from +15V |
| `PG_5V` | TPS2116 PR1, FPGA/RP2350 | 3.24 V when the buck is in regulation, 0 V otherwise (fail-safe) |
| `PG_3V3` | 1V1 EN, 2V5 EN_UV, FPGA B4 | open drain, 100 kΩ to +3V3 |
| `VDRV_EN` | from RP2350 (or FPGA) | active high, 3.3 V, 100 k pull-down: gate drive off by default |
| `VDRV_PG` | to FPGA and RP2350 | high (2.6–2.9 V) only when VDRV ≥ 6.40 V; 0 V when VDRV is absent |
| `AN_OFF` | from RP2350 (optional) | active high forces ±15 V off; 100 k pull-down (on by default) |

## Proposed changes to architecture

1. **Split the 5 V rail into `+5V_BUCK` and `+5V`.** LEDs take `+5V_BUCK` (before the USB OR) via
   the TPS2553 current-limit switch, so LED current never flows through the mux and the LEDs are
   off on USB-only power by construction (R-23). Logic takes `+5V` (the mux output). New nets:
   `+5V_BUCK`, `+5V_LED`.
2. **Replace "two ideal diodes" (R-23) with one TPS2116 priority power mux.** A pair of LM66100
   ideal diodes cross-wired for ORing (their datasheet §9.2.1–9.2.2) turns *both* channels off when
   the two inputs sit at the same voltage, and a 5.05 V buck against a 4.75–5.25 V USB port will do
   that. The TPS2116 in priority mode always takes the buck when `PG_5V` is high, takes USB
   otherwise, blocks reverse current both ways, and takes no USB current while PoE is up, so a PC
   port is never loaded beyond its 500 mA when both are plugged in. It still meets R-23's intent
   (neither source back-feeds the other).
3. **VDRV is a dedicated 7.0 V rail from VBUS (LM5017) into each LMG1210's VIN pin**, not 5 V into
   VDD. LMG1210 VDD abs max is 5.5 V and its bypass-LDO range is 4.75–5.25 V. Running each driver on
   its own internal LDO (6–18 V in, 100 mA) isolates the four drivers from each other and from the
   noisy 5 V LED rail, and gate drive is impossible on USB power. Per-driver LDO loss is 82 mW at
   1 MHz.
4. **Gate drive is default-off in hardware.** The VDRV buck is enabled through its UVLO pin by
   `VDRV_EN`, which firmware asserts only after FPGA DONE, `PD_PG` and VBUS in range (see
   `C-sequencing.md`). `VDRV_PG` reports it back.
5. **Block E rails after the ECP5 switch (2026-11-07)**: `+1V1` (VCC) replaces `+1V2`; `+2V5` (VCCAUX,
   TPS7A9401 from +3V3) is new; `+1V8` is withdrawn. 3V3 and 1V1 use forced-PWM bucks
   (TPS62A02AP) for block E's ≤ 10 mV VCC/PLL ripple limit.
6. **New signals for block E's pin budget**: inputs `PG_5V`, `VDRV_PG`, `LED_FAULT_N`,
   `QWIIC_FAULT_N`; outputs `VDRV_EN`, `LED_EN`, `QWIIC_PWR_EN`, optional `AN_OFF`. These are
   slow, so RP2350 GPIO is fine. `VDRV_PG` should also go to the FPGA so the PWM gate is in logic,
   not firmware.

## Open questions

- Block F loads received 2026-11-07 (+15 V 120 mA design, −15 V 110 mA, 3V3_Q 30 mA, +5V_A 15 mA);
  Fly-Buck and LDOs resized (C-pm15-flybuck.md, C-pm15-ldos.md). 3V3_Q changed to TPS7A9401 for
  ≤ 5 µVrms in band and gated by +15V; block F's flip-flops need Ioff inputs.
- Block D (answered 2026-11-07): IGB070S10S1, 42–79 mA total on VDRV. The 200 mA design is kept as margin. 3V3_A was added for block D's sensing.
- Block E (ECP5, 2026-11-07): +1V1 400 mA design and +2V5 50 mA. The typical 1V1 current is my
  estimate is ≈ 0.25 A (no power-calculator figure yet). +3V3 must stay ≤ 3.465 V (ECP5 VCCIO), so the 3V3 divider
  uses 0.5 % resistors.
- Block B chose an SMCJ58A for VBUS (B-output.md: VBR 64.4 V min; its clamp at rated pulse
  current is higher still). All block C parts are 100 V, so they ride through any TVS-clamped
  transient. This rules out the 85 V LMR38020 alternative noted in `C-5v-buck.md`.

## Signal ownership agreed with block E (E-interfaces.md, ECP5 revision 2026-11-07)

- RP2350 direct: `VDRV_EN` GPIO36 (100 kΩ pull-down, block C); `VDRV_PG` GPIO33 (driven, no
  pull-up needed).
- FPGA inputs (3.3 V bank): `PG_5V` B3 (divided from +5V_BUCK, 3.24 V high, not open drain, so **no
  pull-up**); `PG_3V3` B4 (100 kΩ to +3V3, block C); `LED_FAULT_N` K16 and `QWIIC_FAULT_N` C14 (10 kΩ
  to +3V3, **fitted by block C/G** at the TPS2553s); `VUSB_DET` E14 (3.12 V max divider by block G);
  `PG_3V3Q` → FPGA B5 (bank 0) through block E's 1 kΩ series, with block C's 100 kΩ pull-up.
- FPGA outputs: `LED_EN` H15, `QWIIC_PWR_EN` J16. ECP5 pins default to pull-down, and the 100 kΩ
  pull-downs at both TPS2553 EN pins stay as a backstop.
- The TCA9535 expander is dropped, so I2C address 0x20 is free again.
