# J (DISP) — 8-pin header for a 0.96 in 80×160 ST7735S IPS module (R-20)

Datasheets: datasheets/boomele-1x8-female.pdf (BOOMELE 2.54 mm female header drawing, no text
layer), datasheets/srv05-4.pdf, datasheets/murata-blm18pg.pdf. The FPGA I/O drive figures are from
datasheets/lattice-FPGA-DS-02012.pdf (ECP5 family; LVCMOS33 drive 4/8/12/16 mA, VCCIO ≤ 3.465 V). The FPGA was
changed from GW1NR-9 to ECP5 LFE5U-25F on 2026-11-07.
The module itself (user's, 2026-11-07) has no datasheet on file, so its pin order and backlight
current must be measured on the module in hand (R-20).

| Part | MPN | Supplier line |
|---|---|---|
| 1×8 female header 2.54 mm, TH | 2.54-1*8P (BOOMELE) | `C27438 2.54-1*8P (BOOMELE(Boom Precision Elec), Through Hole,P=2.54mm): extended, JLC stock 122671, lifecycle normal, checked 2026-11-07` |
| ESD ×2 (8 lines, rail +3V3) | SRV05-4.TCT | `C13612 SRV05-4.TCT (SEMTECH, SOT-23-6L): extended, JLC stock 66821, lifecycle normal, checked 2026-11-07` |
| Ferrite on the module VCC (R-90) | BLM18PG221SN1D | `C80165 BLM18PG221SN1D (muRata, 0603): extended, JLC stock 218690, lifecycle normal, checked 2026-11-07` |
| Series R ×8 | 47 Ω 1 % 0402 (basic) | phase 2 |
| Solder jumpers ×24 (GND, VCC, BLK per pin) | 2-pad, PCB only | — |
| Backlight high-side switch | AO3401A + 2N7002 | see below |

## Circuit (every pin remappable)

Each header pin n (1…8) has three possible connections:
- `DISP_n` → 47 Ω → an FPGA I/O (8 FPGA pins total, block E),
- JPn_G (solder jumper, open by default) → GND,
- JPn_V (solder jumper, open by default) → `DISP_VCC` = +3V3 through the BLM18PG221 ferrite.

Default jumpers, for the common order GND, VCC, SCL, SDA, RES, DC, CS, BLK: **JP1_G and JP2_V made
as bridged-by-default jumpers**; all other jumpers open. Rule: **an FPGA pin whose header pin is
jumpered to GND or VCC must be constrained as an input (Hi-Z)**. A driven-high pin into a GND jumper
would source 3.3 V / 47 Ω = 70 mA, which is above the 16 mA maximum drive. The bitstream's pin constraint
file carries the map, and the series R limits damage if it is wrong at the 8 mA drive setting.

ESD: two SRV05-4 at the header (pins 1/3/4/6 of each to four header pins; pin 5 = +3V3 per the
Semtech "option 1" connection; pin 2 GND).

## Calculations

- **Supply**: module ≤ 40 mA including backlight (R-20). The BLM18PG221 is rated 1.4 A with
  ≤ 0.14 Ω, so the drop is 5.6 mV. It comes from the +3V3 budget (C-interfaces.md).
- **Backlight switch (revised 2026-11-07, block E's request)**: a steady 16 mA backlight shouldn't
  load VCCIO2, and a module's backlight current is unknown. So BLK gets a high-side switch instead
  of an FPGA pin:
  - Q1 **AO3401A** P-FET: source = `DISP_VCC` (after the ferrite), drain = `DISP_BLK`, gate pulled up
    to source by 100 kΩ (off).
  - Q2 **2N7002** N-FET pulls Q1's gate low. Q2's gate = `DISP_BL_PWM` (ECP5 ball G15, bank 2,
    4 mA drive, PWM ≤ 2 kHz, block E) through 100 Ω, with a 100 kΩ pull-down, so it is off at power-up (ECP5 pins
    also default to pull-down).
  - **Each header pin gets a third solder jumper JPn_B → `DISP_BLK`** (open by default; JP8_B made
    bridged for the usual BLK-on-pin-8 order). The BLK pin stays remappable like the others, and that
    pin's 47 Ω FPGA line is then constrained Hi-Z.
  - Checks:
    - AO3401A: VGS(th) −0.5…−1.3 V, RDS(on) ≤ 85 mΩ at VGS = −2.5 V (datasheets/aos-ao3401a.pdf). With
      VGS = −3.3 V the drop at 40 mA is ≤ 3.4 mV, so any module backlight up to the R-20 40 mA budget
      (far more if needed: ID 4 A) works.
    - 2N7002: Vth 1.0–2.5 V at 250 µA (datasheets/cj-2n7002.pdf). With a 3.3 V gate it easily sinks
      the 33 µA pull-up current.
    - PWM dimming: off-time constant 100 kΩ × AO3401A gate charge is tens of µs, so keep PWM ≤ 1–2 kHz
      (fine for a backlight). Use a 10 kΩ pull-up if faster PWM is wanted.
  - Parts: `C15127 AO3401A (AOS, SOT-23): basic, JLC stock 1677219, lifecycle normal, checked 2026-11-07`;
    `C8545 2N7002 (JSCJ, SOT-23): basic, JLC stock 5965543, lifecycle normal, checked 2026-11-07`.
  - Signal pins: ECP5 LVCMOS33 drives 4/8/12/16 mA with VOH ≥ VCCIO − 0.4 V
    (datasheets/lattice-FPGA-DS-02012.pdf). Bank 2's DC load without the backlight is small (block E:
    ≈ 17 mA including other users). Pins: bank 2 B16, C16, C15, D16, E15, E16, F15, F16, driven
    directly at 3.3 V.
- **Signal integrity**: ST7735S SPI write clock ≤ 15 MHz typical. 47 Ω × (SRV05-4 3–5 pF + header and
  module ≈ 10 pF + trace) ≈ 0.8 ns τ, insignificant against a 33 ns half-period.
- **Header**: 2.54 mm female, 1×8, through-hole, hand- or JLC-assembled. The module plugs straight in
  (or via a ribbon). Its mechanical drawing is image-only; the pitch and row are standard and are
  checked against KiCad `Connector_PinSocket_2.54mm:PinSocket_1x08_P2.54mm_Vertical` in phase 2.

## Fine print / gotchas

- SRV05-4 with pin 5 on +3V3: while +3V3 is off, the steering diodes would clamp a pin to an off
  rail. The module is powered from the same +3V3, so the two always come up together.
- R-90: ferrite on the display cable supply. The 47 Ω series resistors on the signals act as the EMC
  damping for the data lines.

## Open questions

- **User: confirm the module's pin order** (R-20, before phase 2). It only sets which jumpers are
  bridged by default.
- Phase 2: measure the BLK current on the module (now only a budget check; the switch handles any
  value up to the 40 mA R-20 budget).
- Block E: `DISP_BL_PWM` assigned to G15 (done). The Hi-Z rule for the BLK-jumpered line is recorded in
  block E's gateware notes.
- Block E: assigned bank 2 B16 C16 C15 D16 E15 E16 F15 F16 (done).

## Phase 2 correction (schematic, 2026-11-07)

The switched backlight rail is named **`DISP_BL_SW`** on the schematic (AO3401A drain, JPn_B
jumpers). `DISP_BLK` is already the FPGA line to header position 8 (E-pinmap.md); giving the rail
the same name would have tied the FPGA pin to the switch output. Header position → FPGA line:
1 DISP_AUX7, 2 DISP_AUX8, 3 DISP_SCL, 4 DISP_SDA, 5 DISP_RES, 6 DISP_DC, 7 DISP_CS, 8 DISP_BLK.
