# Design intent — Studio Amp satellite board, variant A

Phase 0. Every item has a number or an explicit "don't care". Source: the system specification
(`PoE++ GaN Speaker Amplifier — System Specification.md`, repo root) plus the user's answers of
2026-11-07. Items marked **(proposed)** are Claude's defaults, which stand unless the user changes
them at sign-off.

Board: `satellite`. First variant: `hw/satellite/a/`.

## Purpose

R-01. A bi-amplified studio-monitor amplifier that mounts inside one speaker. A single Ethernet
cable supplies power (IEEE 802.3bt PoE++) and the network. Two GaN full-bridge (BTL) class-D
channels drive the woofer and the tweeter. An FPGA generates the PWM directly from digital audio
(no analog modulator in this variant). The RP2350 does the network stack, DSP (crossover, EQ, room
correction) and supervision. PTP keeps the speakers in a room sample-synchronous. Personal project
first, packaged to sell later.

R-02. Variant A choices (user, 2026-11-07): an integrated PoE PD chip; an isolated active-clamp
forward converter; a 48 V amp rail; Gowin GW1N-9-class FPGA; all-GaN power stage; satellite only
(no subwoofer); everything on one board (full spec, not a core-only subset); headphone and line
out fed from an FPGA 1-bit stream with a discrete reconstruction filter (no DAC chip); LMG1210 half-bridge
GaN gate drivers in place of the spec's uP1966 (0 LCSC stock).

R-03. Deferred to later variants, with no provision needed in A beyond what is listed:
discrete PD front end, flyback, planar transformer, non-isolated buck, silicon-MOSFET control
stage, self-oscillating (UcD) analog loop, subwoofer board, torture tester.

## Open source or confidential

R-04. Open source, MIT licence. Public repo `github.com/sequoia-hope/studio-amp`; repo URL on
the silkscreen; the pcbview page may be published to GitHub Pages.

## External interfaces

| # | Connector / link | Direction | Signal | Voltage (normal / worst case) | Current (cont. / peak) | Mates with |
|---|---|---|---|---|---|---|
| R-10 | RJ45, 4-pair PoE-rated magnetics, centre taps on all pairs | in (power), bidir (data) | 10/100BASE-TX + 802.3bt Type 3/4 power on all 4 pairs | 0–57 V continuous, either polarity, either pair set; IEC 61000-4-5 1 kV common-mode through the magnetics (verify against 802.3bt clause 145); ESD ±8 kV contact on the shield. Shield to secondary GND through 1 nF / 1 MΩ (no chassis in a wooden cabinet) **(proposed)** | ≤ 71.3 W input (Class 8), ≤ 960 mA per pair-set | Cat5e/6 to a PoE++ switch or injector |
| R-11 | Woofer output, 2-pole | out | BTL PWM, post-LC-filter | ±48 V differential peak; must survive output short to each other and to either rail-side, and back-EMF from the driver | 6 A pk into 8 Ω, 12 A pk into 4 Ω (min load **4 Ω nominal, 3.2 Ω DCR (proposed)**) | Woofer, via a 5.08 mm-pitch 2-pin pluggable terminal block rated ≥ 15 A **(proposed)** |
| R-12 | Tweeter output, 2-pole | out | BTL PWM, post-LC-filter, protective high-pass | as R-11 | as R-11, 4 Ω min **(proposed)** | Tweeter |
| R-13 | Headphone jack | out | stereo analog, discrete class AB on ±15 V | ≥ 5 Vrms into 300–600 Ω (7.1 Vpk, inside the ±15 V rails) **(proposed)**; short-circuit proof | ≤ 25 mA pk | 6.35 mm TRS **(proposed; 3.5 mm alternative)** |
| R-14 | Line out (to powered sub) | out | analog, same DAC path as R-13 | 2 Vrms nominal, ≤ 4 Vrms max **(proposed)**; mono-summed or L/R firmware-selectable | ≤ 10 mA, ≥ 600 Ω load | 3.5 mm TRS or RCA **(proposed: RCA)** |
| R-15 | External measurement mic jack | in | bare electret capsule with plug-in power (bias ~2.5 V via resistor) **(proposed; phantom-powered and USB measurement mics are not supported)** | 0–2 V; survives a line-level source plugged in by mistake | < 1 mA | 3.5 mm TRS |
| R-16 | On-board MEMS mic | in | PDM digital | 3.3 V | — | — |
| R-17 | Knob header | in | RP2350 ADC (clean reference, RC filter) + GPIO for rotary encoders | 0–3.3 V; ESD protected | — | optional-population 0.1 in header |
| R-18 | Qwiic I2C connector, buffered | bidir | I2C, buffer for long runs | 3.3 V | ≤ 300 mA to the LED driver board **(proposed)** | JST SH 4-pin (Qwiic) |
| R-19 | Addressable LED output | out | 5 V level-shifted; WS2812 single-wire or APA102/SK9822 data+clock, firmware-selectable | 5 V | ≤ 1 A (5 W) at Class 8, firmware-limited by PoE class (see R-33a), with a hardware current limit **(proposed)** | one connector, 4-pin (5V, GND, D, C) **(proposed: JST PH)** |
| R-20 | Colour OLED header | out | SPI (SCK, MOSI, RES, DC, CS) routed to the FPGA for remapping; solder jumpers on GND/VCC | 3.3 V | ≤ 50 mA | 7-pin 0.1 in female, SSD1331/SSD1351 module (exact module still open) |
| R-21 | RP2350 debug | bidir | SWD + UART | 3.3 V | — | Raspberry Pi Debug Probe (3-pin JST SH, from Sequoia's library) |
| R-22 | FPGA JTAG | bidir | JTAG | 3.3 V | — | 0.1 in or 1.27 mm header **(proposed)** |
| R-23 | USB-C (RP2350 USB) | bidir | USB 2.0 FS, for bring-up, BOOTSEL and bench audio **(proposed — not in the spec)** | 5 V in. On USB alone only 5 V/3.3 V/1.2 V logic, the FPGA and the PHY come up; VBUS, gate drive and LEDs stay off. USB 5 V joins the 5 V rail through an ideal diode, and the 5 V buck output joins it through another, so neither back-feeds the other | sink ≤ 500 mA | USB-C cable |

All user-reachable conductors (R-11 to R-23) are on the isolated secondary side.

## Power

R-30. Input: PoE++ 802.3bt. **Full performance is specified at Class 6** (51 W at the PD, a Type 3
PSE such as a 60 W PoE++ switch port), since Type 4 / Class 8 PSEs are rarer. The PD requests
Class 8 (71.3 W) and uses the extra as headroom when granted. It also starts and runs reduced
on Type 2 (25.5 W). The granted class is read from the PD chip's type-indication pins (across the
barrier, R-32a) and later from LLDP in RP2350 firmware; firmware sets the amp and LED power limits
from it. MPS is not needed: idle draw is well above the MPS minimum (the spec's MCU-held MPS is
dropped for variant A).

R-31. Input bridges: two MOSFET ideal-diode bridges (one per pair set) **(proposed: discrete or
controller-driven FET bridge, decided in phase 1)**; inrush limiting and UVLO by the PD chip, with
the PD's input capacitance and inrush within the 802.3bt limits (verify in phase 1).

R-32. Isolation: primary to secondary ≥ 1500 Vrms for 60 s (802.3 PoE isolation); the creepage
and clearance this needs is a board keepout across which only the transformer and the R-32a
isolators pass (phase 4).

R-32a. Signals crossing the barrier, through a digital isolator or optocouplers rated for R-32
**(proposed)**: the PD chip's class/type indication (granted power), and PD power-good. PoE loss is
detected on the secondary both from this power-good and from a fast comparator on the converter's
secondary (rectified pulse loss or VBUS droop), whichever trips first. Nothing crosses back to the
primary except the converter's feedback (optocoupler or isolated error amp, phase 1).

R-33. Isolated DC-DC: active-clamp forward, ≥ 92 % efficiency at full load **(proposed target)**,
off-the-shelf wound transformer, fsw chosen in phase 1. VBUS regulation 48 V ± 2 % static; dynamic
sag up to 10 % during bursts. Synchronous rectifiers must not run in reverse: diode emulation or SR
inhibit, so energy returned to VBUS is not pushed back to the primary.

R-33a. Power budget (average; phase 1 recomputes with real part efficiencies):

| | Class 8 | Class 6 (nominal) | Type 2 |
|---|---|---|---|
| Power at PD | 71.3 W | 51.0 W | 25.5 W |
| Bridges + PD + hot-swap loss | −1.5 W | −1.2 W | −0.8 W |
| ACF converter at 92 % | 64.2 W | 45.8 W | 22.7 W |
| Logic: 3.3 V + 1.2 V + PHY + RP2350, through bucks (≈ 2.5 W load) | −2.9 W | −2.9 W | −2.9 W |
| Gate drive, 4 half-bridges at ≤ 1 MHz | −1.0 W | −1.0 W | −1.0 W |
| ±15 V analog (≤ 80 mA per rail load) | −2.8 W | −2.8 W | −2.8 W |
| LEDs, firmware limit | −5.8 W (5 W load) | −2.3 W (2 W) | 0 W (off) |
| **Left for VBUS to the bridges** | **51.7 W** | **36.8 W** | **16.0 W** |
| Average output to speakers at 90 % amp efficiency | ≈ 46 W | ≈ 33 W | ≈ 14 W |

Peaks above these averages come from the VBUS bulk capacitance.

| Rail | Voltage | Load (avg / peak) | Notes |
|---|---|---|---|
| VBUS (amp) | 48 V | per R-33a / 3.3 A pk from the bulk | bulk capacitance for a combined 144 W, 10 ms burst at ≤ 10 % sag: ≈ 1.1 J deficit (with ~50 W from the converter) → **≈ 5 mF, rising to ≈ 7 mF if the converter current-limits**; 63 V, 105 °C electrolytics, ripple current set in phase 1. That is about 5–7 cans of 16 × 25 mm, which phase 4 must place. Bus-voltage feedforward via a fast ADC |
| ±15 V analog | ±15 V | ≤ 80 mA per rail | topology decided in phase 1: an extra forward-converter winding needs its own output inductors and cross-regulates poorly; the alternative is derived from VBUS or 5 V on the secondary. Post-regulated (LDO or cap multiplier) |
| 5 V | 5 V | ≤ 1.8 A (LEDs 1 A, gate drivers, logic bucks, USB sink) | buck from VBUS |
| 3.3 V | 3.3 V | ≤ 600 mA | buck; a separate quiet 3.3 V LDO for the 1-bit DAC reclocking flip-flop and the analog reference |
| 1.2 V | FPGA core | per GW1N(R)-9 datasheet (phase 1) | buck or LDO |
| 1.1 V | RP2350 core | from the RP2350's internal regulator | |
| Gate drive | per gate-driver datasheet (GaN gate abs-max ≈ 6 V, verify) | 4 half-bridges | regulated, from 5 V or a dedicated rail, phase 1 |

R-34. Sequencing: the amp stays muted until VBUS and the gate supply are valid and the FPGA has
configured; pop-free start and stop. On PoE loss (R-32a) the FPGA ramps the output to zero within
≤ 5 ms, then stops switching. Hold-up: ≥ 20 ms of logic, gate-drive and analog rails (≈ 8 W, with
the output stage at zero) after PoE loss, from the VBUS bulk capacitance (far more than the ≈ 1 mF
this needs).

R-35. Backfeed: in BTL, supply pumping largely cancels; what comes back is driver back-EMF and
energy stored in the output filters. VBUS bulk absorbs it, the SRs cannot pass it back (R-33), and
a TVS clamp on VBUS (≈ 56–58 V stand-off, below the 100 V GaN rating) handles transients only, not
sustained regen. Firmware stops switching if VBUS exceeds 55 V **(proposed)**.

## Environment

R-40. Indoor, inside a sealed speaker cabinet. Room 0–35 °C; air inside the cabinet up to 55 °C
at sustained full power **(proposed)**. Parts rated ≥ 85 °C ambient; all electrolytics 105 °C
with ripple-current derating; GaN Tj ≤ 125 °C at 55 °C internal air.

R-41. Vibration: mounted to a loudspeaker back panel at high SPL. Large parts (inductors,
transformer, bulk caps) are mechanically secured (adhesive or through-hole); no tall unsupported
parts **(proposed)**.

R-42. ESD: the externally reachable connectors (RJ45, headphone, line out, ext. mic, USB-C) protected
to IEC 61000-4-2 ±8 kV contact; inward-facing headers (knob, Qwiic, LED, OLED, debug) get series
resistors and light TVS only **(proposed)**. Humidity: don't care beyond normal indoor.

## Performance targets

R-50. Output power: ≥ 100 W peak into 8 Ω per channel (144 W theoretical at 48 V BTL; 288 W
into 4 Ω). Firmware limits each channel to **≤ 144 W / 12 A peak** whatever the load, and the
hardware overcurrent trip (R-54) sits at ≈ 15 A. Long-term average is limited by R-33a (≈ 33 W to
the two channels at Class 6, ≈ 46 W at Class 8).

R-51. Speaker-output audio, 8 Ω, 20 Hz–20 kHz. Variant A is **open-loop digital PWM with
bus-voltage feedforward only**, so its targets are set for that **(proposed)**: THD+N ≤ 0.1 % at
1 W and ≤ 0.3 % at 50 W; output noise ≤ 150 µV A-weighted; frequency response don't care, because
it is load-dependent through the LC filter and corrected in DSP for the known driver. The board
also carries an optional-population post-filter sense path (output voltage, divided, into an ADC
read by the FPGA), so a closed-loop variant can reach studio-monitor numbers (THD+N ≤ 0.02 %,
≤ 60 µV) without a respin.

R-52. Headphone/line out **(proposed)**: THD+N ≤ 0.01 % at 1 Vrms; noise ≤ 10 µV A-weighted. Proved
by simulation of the 1-bit stream plus reconstruction filter in phase 8.

R-53. PWM: switching frequency 400 kHz–1 MHz, tunable per build; three-level BD modulation;
noise shaping that pushes quantization noise above 20 kHz; edge resolution set in phase 1 from the
noise-shaper analysis (target ≤ 1 ns effective, using PLL/DDR I/O). Output LC filter sized in
phase 1 jointly with the noise-shaper order.

R-54. Protection: cycle-by-cycle overcurrent shutdown at ≈ 15 A with ≤ 200 ns from threshold to
all gates off **(proposed)**; DC-at-output detection that shuts the bridge down (all four FETs
off, no relay) in ≤ 100 ms; over-temperature
on the GaN and the inductors; tweeter protective high-pass in hardware, a series film capacitor,
so the tweeter is protected even if the bridge fails shorted.

R-55. Network and sync: 10/100 Ethernet over RMII (PHY to FPGA MAC); PTP IEEE 1588 with hardware
timestamps in the FPGA; speaker-to-speaker offset ≤ 10 µs in a room, ≤ 1 ms across rooms. Audio
clock disciplined to PTP: VCXO trim or fractional resampler in the FPGA, chosen in phase 1 (a VCXO
is a BOM part; the resampler costs FPGA resources). A GPIO test point toggles on the PTP second for scope verification.

R-56. Firmware updates: A/B images with rollback, over the network, for both the RP2350 and the
FPGA bitstream. 16 MB of QSPI flash holding two RP2350 images and two FPGA bitstreams **(proposed;
bitstream size checked in phase 1)**.

## Mechanical

R-60. Outline free; Claude proposes one in phase 4 (expected about 100–130 mm square), and the
enclosure is designed around it in Waffle Iron. Mounts to the speaker back panel with 4 × M3
**(proposed)**. Connectors on edges reachable from the back panel cut-out: RJ45, headphone, line
out, ext. mic, USB-C; speaker outputs and internal headers face inward.

R-61. Thermal: GaN and inductor heat goes into the board copper and from there to the back panel
(thermal pad or aluminium plate under the GaN), sized in phase 4.

R-62. Height: don't care on the inward side; the back-panel side is limited by its standoff
height, set in phase 4.

## Manufacturing

R-70. Fab and assembler: JLCPCB. Quantity: 5 prototypes. Parts on both sides allowed. ≥ 4 layers,
6 if the isolation and power-stage layout need it (decided in phase 5). Cost is secondary to
performance on this spin; no per-board cost target. Parts from LCSC; JLC-assembled except for
large through-hole parts (transformer, bulk caps, jacks), which may be hand-soldered.

## Serviceability

R-80. A development board: designators on every part where they fit; test points on every rail,
every switch node (with a scope-probe ground spring nearby), VBUS, the PTP-second GPIO and the
1-bit DAC stream; 0 Ω or solder-bridge isolation links between the power, amp, logic and analog
sections for bring-up.

## Compliance

R-90. No formal certification on this spin. Designed for FCC Part 15 Class B / CE EMC from the
start: spread-spectrum or programmable fsw, an output LC with common-mode control, Ethernet
common-mode chokes / Bob Smith termination, ferrites on the LED and display cables. 802.3 PoE
isolation per R-32.

## Known risks and open questions

R-95. To resolve in phase 1 (part audits). LCSC stock checked 2026-11-07 with `jlc_parts.py`:
- PD chip: KTA1142 has 0 stock and TPS23730/1 (PD + DC-DC) have 0 and 3, so the plan is
  **TPS2373-4RGWR (C470963, 481 in stock)** plus a separate active-clamp forward controller,
  **UCC2897A** (C54444 TSSOP-20, 3944 in stock). Both still need their datasheet audits.
- FPGA: the only GW1N(R)-9 in stock is **GW1NR-LV9QN88PC6/I5 (C5799578, 124)**, the Tang Nano 9K
  part. Confirm Apicula support, I/O count (PHY + 8 PWM + OLED + RP2350 link + mic) and
  PLL/DDR edge resolution. Every GW1N-LV9 listing shows 0 stock.
- Gate driver: **uP1966E has 0 stock** on every LCSC listing. **User chose LMG1210RVRR**
  (C2677136, 2841 in stock) on 2026-11-07: one half-bridge GaN driver per leg pair, 4 per board.
- GaN: Innoscience INN100EBD018DAD-C (C54350158, 1076), INN100EBD025DAD (839), INN100EA035A-C
  (859), against 12 A peak and the thermal path; lifecycle not reported by LCSC, so check it by hand.
- PHY: RTL8201F-VB-CG (C45044, 42934) and LAN8720AI (C17146, 9257) are both plentiful; **JL1101
  has 0 stock**, so it is not a usable second source.
- The RP2350–FPGA link for network frames and audio (QSPI-style, PIO parallel or SPI), and its
  bandwidth.
- Forward transformer: an off-the-shelf part for 70 W, 42–57 V in, 48 V out (and the ±15 V
  decision in R-33a), otherwise a custom part, which conflicts with the sourcing rule.
- VBUS bulk: ≈ 5–7 mF, 63 V, 105 °C, ripple current, volume.

R-96. Open with the user:
- the exact OLED module (pinout, R-20);
- ~~the gate driver~~: LMG1210 (user, 2026-11-07);
- ~~the R-51 audio targets~~: relaxed open-loop targets accepted (user, 2026-11-07);
- ~~confirm the **proposed** items~~ (signed off 2026-11-07, as written):: 4 Ω minimum load with a 144 W / 12 A firmware limit (R-11, R-50),
  a 6.35 mm headphone jack at 5 Vrms (R-13), RCA line out (R-14), USB-C port (R-23), a 5 W LED
  budget at Class 8 (R-19), and full performance specified at Class 6 (R-30).
