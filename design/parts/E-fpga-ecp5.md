# U (FPGA) — Lattice ECP5 LFE5U-25F-7BG256I

Replaces the GW1NR-9 (user, 2026-11-07; `E-fpga-gw1nr9.md` is kept, marked superseded).

Datasheets (read for the sections cited; text extracted with pdftotext):
- `datasheets/lattice-FPGA-DS-02012.pdf`: ECP5/ECP5-5G Family Data Sheet, FPGA-DS-02012-3.4 (Sep 2025). Read: §1 (selection guide Tab 1.1), §2.11 PIO and DDR gearing, §2.14 sysI/O (power-up, hot socketing), §3.1–3.10 (abs max, recommended operating, ramp, POR, power-up sequence, hot socketing, DC, static current), §3.18 external switching (Tab 3.22, GDDR tables), §3.19 PLL (Tab 3.23), §3.31 sysCONFIG timing (Tab 3.42), ordering. `datasheets/ecp5-lcsc.pdf` is LCSC's copy (rev 2.2), kept as the supplier record.
- `datasheets/lattice-FPGA-TN-02039.pdf`: sysCONFIG User Guide, FPGA-TN-02039-2.6 (Oct 2026). Read: §4 (bitstream sizes Tab 4.1, status register, ports, sysCONFIG pins Tab 4.5, CFGMDN Tab 4.6, PROGRAMN/INITN/DONE), §6.2 slave SPI (pins Tab 6.3, timing, commands), §8 (wake-up), GPIO default state (§5).
- `datasheets/lattice-FPGA-TN-02038.pdf`: Hardware Checklist, FPGA-TN-02038-2.1. Read: all (supplies, filtering Tab 3.1, capacitors, sequencing, configuration pins Tab 6.1–6.3, I/O, layout).
- `datasheets/lattice-FPGA-TN-02035.pdf`: High-Speed I/O Interface, FPGA-TN-02035-1.3. Read: gearing overview, ODDRX2F, ECLKSYNCB/CLKDIVF, DELAYF/DELAYG (§8).
- `datasheets/lattice-FPGA-TN-02200.pdf` (sysCLOCK PLL, FPGA-TN-02200-1.4) and `datasheets/lattice-FPGA-TN-02032.pdf` (sysI/O, FPGA-TN-02032-1.4): used for the PLL and I/O references.
- `datasheets/lattice-FPGA-DS-02053-packages.pdf`: Package Diagrams, FPGA-DS-02053-8.8, §94 "256-Ball BBG/caBGA: MachXO3, MachXO2, ECP5".
- `datasheets/lattice-ECP5U-25-pinout.csv`: ECP5U-25 pinout (Lattice, rev 2.0, 2021-09-17), CABGA256 column. Every ball in `E-pinmap.md` was checked against it by script.

MPN: LFE5U-25F-7BG256I (24k LUT, speed grade −7, caBGA-256, industrial)
Supplier: `C1550762 LFE5U-25F-7BG256I (Lattice, CABGA-256): extended, JLC stock 1125, lifecycle normal, checked 2026-11-07`. Need 7. Other 25F caBGA-256 grades are not orderable in quantity: −8 has 5 in stock (C1551775), −6 has 9 (C5272996).
Footprint: 14 × 14 mm caBGA, 16 × 16 balls, **0.80 mm pitch**, ball Ø 0.40–0.50 mm (0.45 nom), height ≤ 1.70 mm (DS-02053 §94, JEDEC MO-275 JJAB-2). See the fan-out section below.

## Resources (DS-02012 Tab 1.1)

24k LUTs, 56 × 18 kb sysMEM (1,008 kb), 194 kb distributed RAM, 28 18×18 multipliers, 2 PLLs + 2 DLLs, no SerDes (LFE5U). caBGA-256: 197 user I/O (CSV: banks 0 = 24, 1 = 32, 2 = 32, 3 = 32, 6 = 32, 7 = 32, 8 = 13 + PROGRAMN).
That is more than the Gowin (8.6k LUT, 20 multipliers), with room for the noise shaper, MAC/PTP, a 4-tap FIR DAC ×2 and, if ever needed, a resampler.

## Absolute max vs our worst case (DS-02012 Tab 3.1, 3.2)

| Parameter | Abs max | Recommended | Ours | OK |
|---|---|---|---|---|
| VCC (core) | 1.32 V | **1.045–1.155 V** (1.1 V ± 5 %, noise included) | `+1V1` | regulator ≤ 3 % (TN-02038 §2.2) |
| VCCAUX | 2.75 V | **2.375–2.625 V**; ramp ≤ 30 mV/µs (note 4) | `+2V5` (new rail) | OK |
| VCCIO0–3, 6–8 | 3.63 V | **1.14–3.465 V** | `+3V3`, all banks | 3.3 V + 5 % = 3.465 V is the ceiling: block C must hold `+3V3` within ±3 % including ripple |
| I/O voltage applied | 3.63 V | | 3.3 V logic | OK |
| Tj | 125 °C | −40…+100 °C (I) | < 70 °C (< 1 W, below) | OK |

No 1.8 V or 1.2 V rail is needed by this block any more (`E-interfaces.md`).

## Power-up, sequencing and hot socketing

- POR is released when VCC ≥ 0.90–1.00 V, VCCAUX ≥ 2.00–2.20 V and VCCIO8 ≥ 0.95–1.06 V (Tab 3.4). Supplies must be **monotonic, 0.01–10 V/ms** (Tab 3.3). VCCAUX ≤ 30 mV/µs.
- **VCCIO before or together with VCC and VCCAUX** (TN-02038 §4; DS §2.14.2). Block C brings `+3V3` up first and chains `+1V1` from 3V3 PG, which meets this.
- tICFG ≤ 33 ms from the last of VCC/VCCAUX/VCCIO8 to INITN↑ (Tab 3.42).
- **GPIO default at power-up and during configuration: outputs tri-stated, weak pull-down** (30–150 µA; TN-02039 §5.2 Initialization; TN-02038 Tab 9.1). After configuration, unused pins stay tri-state with pull-down. Bank-8 D[7:0] have no pull. **Consequence:** PWM and enable inputs default low by themselves. Block D keeps its pull-downs as a backstop; they no longer have to beat a pull-up. Active-low selects (ADC CS) get 4.7 kΩ pull-ups so the ADCs stay deselected and don't drive MISO before configuration.
- **Hot socketing (DS §3.6, Tab 3.5).** Left/right banks (2, 3, 6, 7) do not support hot socketing: an input above VCCIO is a low-impedance path to ground. Also, while VCCIO is up but VCC is below its POR trip, **A/B and C/D pin pairs present a low-impedance path between the two pins** (IDK up to ±33 mA, "device damage may occur"). Top/bottom banks (0, 1, 8) are limited to ±1 mA. Because `+1V1` follows `+3V3` by ~1 ms, the board does pass through that window. Rules used in `E-pinmap.md`:
  1. Inputs driven by always-powered parts (isolator, PG, comparators, mics, ADC, faults) go on **top banks 0/1** where possible.
  2. Where such an input has to sit on a left/right bank, its pair partner is **left unconnected** and the input has a series resistor (330 Ω fast, 1 kΩ slow).
  3. Lines the RP2350 drives (link, SSPI) are driven only after the RP2350 sees the rails good (firmware rule).

## Configuration: slave SPI from the RP2350 (the architecture's original plan)

TN-02039 Tab 4.6: **CFGMDN[2:0] = 001 → SSPI**. Pins (CSV / Tab 6.3, all bank 8, powered from VCCIO8 = 3.3 V):

| Function | Ball | Connection |
|---|---|---|
| CCLK (input in SSPI) | N9 | RP2350 SPI1 SCK (GPIO26), 33 Ω series at the RP2350 |
| MOSI (D0) | T8 | RP2350 SPI1 TX (GPIO27) |
| MISO (D1) | T7 | RP2350 SPI1 RX (GPIO24) |
| SN (CSN) | R8 | RP2350 GPIO25, **4.7 kΩ pull-up** (Tab 4.5 note 1, Tab 6.3 note 1) |
| HOLDN | N8 | 4.7 kΩ pull-up, not driven ("do not assert while shifting commands") |
| PROGRAMN | R9 | 4.7 kΩ pull-up to VCCIO8 (TN-02038 Tab 6.2); RP2350 GPIO22 open-drain; low pulse ≥ 110 ns (tPRGM), < 50 ns rejected |
| INITN | T9 | 4.7 kΩ pull-up; RP2350 GPIO23 reads it (open-drain, low = clearing/error) |
| DONE | P9 | 4.7 kΩ pull-up; RP2350 GPIO28 reads it |
| CFGMDN0 / 1 / 2 | N10 / P10 / R10 | CFG0 4.7 kΩ to VCCIO8; CFG1 and CFG2 to GND (< 500 Ω or direct, TN-02039 §4.6.1) |
| JTAG TCK / TDI / TDO / TMS | T10 / R11 / M10 / T11 | to the R-22 header only (3.3 V, VCCIO8): TCK 4.7 kΩ pull-down, TDI/TMS/TDO 4.7 kΩ pull-ups (TN-02038 Tab 6.1). JTAG works regardless of CFG. |

SSPI timing (DS Tab 3.42): fCCLK ≤ **60 MHz**, high/low ≥ 6 ns, setup/hold 1 ns, CCLK↓→MISO ≤ 10 ns, SN high ≥ 25 ns, SN setup/hold 3 ns. Data in on CCLK↑, out on CCLK↓ (§6.2) = SPI mode 0. We run 37.5 MHz (RP2350 clk_peri 150 MHz / 4).
Load flow (the same as Linux `drivers/fpga/lattice-sysconfig.c`, which drives ECP5 sysCONFIG over SPI at up to 60 MHz, `ecp5_spi_max_speed_hz = 60000000`): **tri-state the link pins (GPIO8–19)** → pulse PROGRAMN (≥ 110 ns) → wait INITN high → ISC_ENABLE 0xC6 → ISC_ERASE 0x0E → LSC_INIT_ADDR 0x46 → LSC_BITSTREAM_BURST 0x7A + bitstream → ISC_DISABLE 0x26 → poll LSC_READ_STATUS 0x3C for DONE (bit 8) / FAIL (bit 13) and DONE pin high.
Load time: 5.42 Mb / 37.5 MHz = **0.145 s** worst case (uncompressed, max EBR init).
**SSPI read speed (review MINOR-3):** writes close easily (13.3 ns half-period vs 1 ns setup). A read round trip is ≈ RP2350 SCK pad 3–4 ns (assumed) + 33 Ω/1 kΩ RC 0.4 ns + tSTCO ≤ 10 ns + flight 0.3 ns + RP2350 input ≈ 2 ns ≈ 16 ns, which is longer than a 13.3 ns half-period. **Firmware rule:** read commands (LSC_READ_STATUS 0x3C, IDCODE, busy polls) at ≤ 18.75 MHz (clk_peri / 8); LSC_BITSTREAM_BURST (write-only) at 37.5 MHz.
**PROGRAMN drive (NOTE-7):** the RP2350 "open-drain" on GPIO22 is emulated: the output value is held at 0 and only the output enable toggles. The same applies to INITN/DONE reads.
**Bitstream size (TN-02039 Tab 4.1): LFE5-25, max EBR, uncompressed = 5.42 Mb = 677.5 KB** (4.45 Mb with no EBR init). Two 1 MB slots + two 6 MB RP2350 images = 14 MB of 16 MB → **R-56 holds**, with 2 MB left for config/calibration (`E-flash-w25q128.md`). `ecppack --compress` (Trellis option) shrinks it further.
Persistence: a slave-SPI port kept alive by persistence "is capable of reading commands only … is not a configuration port" (TN-02039 §6.2.1). **Every re-load therefore starts with a PROGRAMN pulse** (GPIO22), never with REFRESH from user mode. The design sets `SYSCONFIG SLAVE_SPI_PORT=ENABLE` only so the RP2350 can read status/ID in user mode in the LPF; nextpnr-ecp5 accepts `SYSCONFIG` keys (`ecp5/lpf.cc`: SLAVE_SPI_PORT, MASTER_SPI_PORT, CONFIG_IOVOLTAGE, …). Set `CONFIG_IOVOLTAGE=3.3`.
No golden image, no JTAG loader, no translators: the Gowin workarounds are gone. Recovery: the RP2350 always holds a known-good bitstream (A/B with rollback); if both are bad, the RP2350 still boots, and USB or the debug probe can rewrite the flash.

## Clocking, PWM gearing and edge resolution

- PLL (DS Tab 3.23): fIN 8–400 MHz, **fVCO 400–800 MHz**, fOUT 3.125–400 MHz, fPFD 10–400 MHz, lock ≤ 15 ms; **output period jitter ≤ 100 ps p-p, cycle-to-cycle ≤ 200 ps p-p (fOUT ≥ 100 MHz)**, phase jitter ≤ 200 ps p-p (fPFD ≥ 100 MHz) or 0.011 UI (< 100 MHz); clean reference, no I/O toggling (note 1). This is tighter than the Gowin's < 300 ps.
- Generic DDRX2 output (ODDRX2F, 4:1) on the **left and right sides only** ("available on each pin on the left and right", TN-02035 §8.7; DS §2.11.2 Fig 2.20). Top banks have ODDRX1F only; **bank 8 (bottom) has no DDR registers at all** on non-SerDes parts (TN-02035 §8.7). The only datasheet limits are **commercial**: DS-02012 Tab 3.22 is "over recommended commercial operating conditions", and its note says "Industrial numbers are typically slower and can be extracted from the Diamond software". At −7 commercial: GDDRX2_TX 700 Mb/s, ECLK (fMAX_EDGE) 350 MHz; edge-clock skew within a bank ≤ 180 ps. No industrial figure is in hand for the −7**I** part.
- **Baseline (review MAJOR-1): PLL ×12.** VCXO 24.576 MHz into **LLC_GPLL0T_IN (P6, bank 6)** → CLKOP = 24.576 × 12 = **294.912 MHz** (VCO 589.824 MHz with CLKOP divider 2; PFD 24.576 MHz) → ECLKSYNCB → ODDRX2F on the 4 PWM pins → **589.824 Mb/s, edge grid 1.695 ns**, 84 % of the commercial ECLK and GDDRX2 limits. CLKDIVF /2 → SCLK 147.456 MHz for the PWM logic.
- **Bring-up option: ×14** (CLKOP 344.064 MHz, 688.128 Mb/s, 1.453 ns, 98 % of the commercial limit). Use it only after characterising it on the boards over temperature, or after the −7I numbers have been extracted from Lattice Diamond (free licence) and recorded here.
- Both settings miss R-53's "≤ 1 ns" physical target; the Gowin reached 1.017 ns. The effective in-band resolution is the noise shaper's job. At fixed shaper order and fsw, 1.695 ns adds 20 log(1.695/1.017) = 4.4 dB of raw quantisation noise against 1.017 ns (1.3 dB against 1.453 ns). Other routes:
  - a −8 part (800 Mb/s commercial) has 5 in stock;
  - DELAYF (128 × ~25 ps, TN-02035 §8) deskews pins but can't place each edge independently.
- **Allowed PWM frequencies on the ×12 grid** (fsw = 589.824 Mb/s / N, R-53 window 400 kHz–1 MHz):

  | N (steps/period) | fsw | fsw / 48 kHz |
  |---|---|---|
  | 1024 | **576 kHz** | 12 (integer) |
  | 768 | **768 kHz** | 16 (integer) |
  | 1316 | 448.2 kHz | 9.337 (= 3072/329, not integer) |
  | 1229 | 479.9 kHz | not integer |

  **448 kHz is not reachable audio-locked on ×12.** 589.824 MHz / 448 kHz = 1316.57 isn't an integer. With other multipliers, an exact 448 kHz needs a PLL input divider of 7, which puts the PFD at 3.5 MHz, below its 10 MHz minimum. The integer-ratio choices inside R-53 are **576 kHz** (lowest) and 768 kHz. 448.2 kHz (N = 1316) is possible only if the modulator accepts a non-integer fsw/fs ratio (a 3072/329 polyphase interpolator in gateware: feasible, more BSRAM and logic; not recommended). 384 kHz (N = 1536, 8 × 48 kHz) is outside R-53's 400 kHz floor.
  On the ×14 option: 448 kHz (N = 1536), 512 kHz (1344), 672 kHz (1024) remain.
- Jitter → noise: the formula and BD common-mode argument in `E-clk-audio-vcxo.md` still hold. The datasheet's 100 ps p-p period jitter is ≈ 15 ps rms if Gaussian over the 10,000-sample measurement — an estimate, not a datasheet figure. The common part cancels in BD.
- RMII: 50 MHz into **PCLKT1_0 (C8, top bank 1)**. The right-hand PLL is unused; its input pad P11 serves as a plain input (`HP_FAULT_N`).
- Fabric at 147.5 MHz (×12; 172 MHz on ×14): fMAX_PRI (primary clock tree) is 303 MHz at −7 commercial (Tab 3.22); the PWM comparator/serialiser path must be pipelined. The noise shaper itself runs at the PWM rate (≤ 1 MHz) with the 28 multipliers.

## I/O and timing numbers used elsewhere (DS Tab 3.22, −7)

Generic SDR with a dedicated primary clock input, no PLL: **tCO ≤ 6.1 ns, tSU ≥ 0 ns, tH ≥ 3.0 ns; with input delay tSU_DEL ≥ 1.33 ns, tH_DEL ≥ 0 ns**; fMAX_IO 350 MHz.
**Caveats (review MAJOR-1, NOTE-2):** these are commercial-grade numbers (Tab 3.22 header) for LVCMOS25, 12 mA, fast slew, 0 pF load (note p.69). For our −7I part at LVCMOS33 into 10–15 pF, allow tCO ≈ 6.1 + 2 = 8 ns. Every budget that uses it keeps ≥ 4 ns of slack after that allowance: RMII TX setup +9.7 → +7.7 ns; link read sample margin +9.6 → +7.6 ns; DAC launch ≤ 8 ns against block F's 12 ns. RMII RX uses tSU_DEL/tH_DEL, where an industrial derating eats into +4.5/+3.2 ns.
- RMII RX: PHY tohold 3.0 ns vs FPGA tH 3.0 ns → without delay the hold slack is 3.4 − (0.2 clock flight + 3.0) = +0.2 ns, so use the input delay (DELAYG): setup slack 20 + 0.2 − 14.4 − 1.33 = +4.5 ns, hold 3.4 − 0.2 = +3.2 ns. TX: 20.2 − (0.2 + 6.1 + 0.2) − 4.0 = **+9.7 ns** setup; hold relies on min tCO (not specified) > 1.3 ns: check the nextpnr timing report (`E-clk-rmii-50mhz.md`).
- DAC launch (block F asks ≤ 12 ns): ≤ 6.1 ns from the clock pin; less from a PLL output.
- Link reads (`E-link.md`): FPGA tCO ≤ 6.1 ns.

## Power (DS Tab 3.8 static; dynamic estimated)

Static typ (TJ 85 °C, nominal supplies, outputs tri-stated): **ICC 77 mA, ICCAUX 16 mA, ICCIO 0.5 mA per bank**. Peak start-up and dynamic currents need the Lattice Power Calculator (Diamond), not available in the open flow; it can be run once on the synthesised design. Estimate for ~60 % LUT use at 100–172 MHz plus PLLs and 8 DDR outputs: **VCC ≈ 250 mA typ, 400 mA design**; VCCAUX **50 mA design**; VCCIO, all banks, **50 mA design**. Power < 0.8 W → Tj rise is small, not a thermal problem.

## Required external parts (TN-02038 Tab 3.1, 6.1–6.3) → `E-fpga-ecp5-passives.md`

- VCC: 3 × 10 µF + 100 nF per pin (6 pins).
- VCCAUX: **120 Ω @ 100 MHz bead + 10 µF + 100 nF per pin** (2 pins); PLL rails target < 0.25 % peak noise (TN-02038 §2.2).
- VCCIO0–3, 6, 7, 8: 10 µF per bank + 100 nF per pin (13 pins); bank 6 (PWM) gets 22 µF ("banks with lots of outputs").
- Configuration and JTAG pull resistors as tabulated above; CCLK series 33 Ω (Tab 6.2 note: 22–80 Ω, at the driver).
- Capacitor voltage ≥ 1.8 × rail (TN-02038 §3.5.2): 6.3 V minimum on 3.3 V → we use 10/16 V.

## Fan-out (caBGA-256, 0.8 mm) against JLCPCB's limits

JLC (capabilities page, checked 2026-11-07): multilayer via 0.15 mm hole / 0.25 mm pad minimum. **Surcharge for 0.10/0.15 mm holes, or for 0.20/0.25 mm holes with pads < 0.45 mm.** BGA pad ≥ 0.20 mm; BGA pad-to-trace ≥ 0.10 mm (0.09 mm multilayer); 1 oz trace/space 0.09/0.09 mm ("3 mil acceptable in BGA fan-outs"); via-in-pad (filled and capped) is a separate process, "default for 6-layer and above".

Geometry with **NSMD ball pads Ø 0.40 mm** (≈ 0.9 × ball) and **dog-bone vias 0.20 mm hole / 0.45 mm pad** (the smallest no-surcharge via):
- Via at the centre of four balls: distance to each ball 0.8 × √2 / 2 = 0.566 mm; copper gap = 0.566 − 0.20 − 0.225 = **0.141 mm** ≥ 0.10 mm. OK.
- Between two ball pads: 0.80 − 0.40 = 0.40 mm → one 0.09 mm trace with 0.155 mm each side. OK.
- Between two dog-bone vias: 0.80 − 0.45 = 0.35 mm → one 0.09 mm trace with 0.13 mm each side. OK.
- **Via-in-pad is not needed.** No surcharge feature is needed either (0.20/0.45 vias, 0.09/0.09 mm only inside the BGA field, ENIG not required for 0.40 mm pads).

Escape depth: one trace per channel escapes about two rings per signal layer. The signal balls chosen sit in rings 0–3, except bank-8 configuration/JTAG/D-pins that the silicon fixes in rings 3–4 (TDO M10, D2 M7, DOUT M8, WRITEN M9). Inner rings 5–7 are power and GND, which go straight down by via to planes.
- Top layer: rings 0–1.
- One inner signal layer: rings 2–3.
- A second inner signal layer, or the bottom: ring 4 and the bank-8 group.
- **Recommendation: 6 layers** (R-70 already allows 6). A 4-layer board is possible only by escaping rings 2–4 on the bottom layer, which then can't carry the BGA's decoupling capacitors under the package. With 6 layers the decaps sit on the bottom under the ball field, between the dog-bone vias, as on Lattice's evaluation boards.

## Fine print / gotchas

- ODDRX2F/ODDR71 exist on left/right banks only; the PWM must stay in banks 6/7 (or 2/3).
- "All supplies with same voltage … should be connected together" (Tab 3.2 note 2): every VCCIO on the one `+3V3`, all VCC pins together.
- Unused VCCIO banks must still be powered (TN-02038 §3.6): all are used here.
- Bank 8 sets the configuration-pin voltage; VCCIO8 = 3.3 V matches the RP2350.
- PROGRAMN must not see a falling edge while the FPGA is in initialisation, and must not be pulled low before all rails are stable (TN-02039 §4.6.2). **Firmware gate (re-review MINOR-4):** the RP2350 has no 1V1/2V5 power-good of its own, so it waits for **INITN (GPIO23) high**. That means VCC, VCCAUX and VCCIO8 are above POR and initialisation is done (tICFG ≤ 33 ms). It then waits a fixed **≥ 10 ms** before the first PROGRAMN pulse, and applies the same gate before every A/B reload.
- Top-side inputs support IDDRX1 only; RMII and the link are SDR, fine anywhere.
- −7 speed grade: GDDRX2 at 700 Mb/s is the binding limit for PWM edge resolution.

## Open-toolchain support (sources checked 2026-11-07)

- **Project Trellis** README: "supports all ECP5 devices"; working: logic, distributed RAM, interconnect, "Basic IO … LPF files and DDR inputs/outputs", block RAM (DP16KD), multipliers (MULT18X18D manual instantiation), global networks, PLLs, DCUs. Tested boards listed include the Lattice ECP5 Evaluation Board, the ECP5-5G Versa kit and the ULX3S. `ecppack` options: `--compress`, `--freq`, `--spimode`, `--usercode`, `--svf`.
- **nextpnr-ecp5** `ecp5/docs/primitives.md`: ODDRX1F, **ODDRX2F** (generic 4:1 output DDR), IDDRX2F, ODDR71B, OSHX2A, **ECLKSYNCB**, **CLKDIVF**, **DELAYF/DELAYG**, **EHXPLLL**, DDRDLLA, DQSBUFM, MULT18X18D ("cascade functionality not supported"). The LPF `SYSCONFIG` keys are listed above.
- **openFPGALoader** `doc/FPGAs.yml`: ECP5 LFE5U-12/25/45/85: memory OK, flash OK (over JTAG; useful on the bench with the R-22 header).
- **Linux** `drivers/fpga/lattice-sysconfig{,-spi}.c`: an open reference implementation of ECP5 slave-SPI configuration (opcodes above) to port to RP2350 firmware.

## Open questions

- Dynamic power: run the Lattice Power Calculator once on the real design, or measure on an evaluation board.
- Min tCO for the RMII TX hold check comes from the nextpnr timing model.
- Edge grid 1.695 ns (×12 baseline) at fsw 576 kHz: the noise-shaper estimate in `E-interfaces.md` shows edge quantisation isn't the noise limiter.
