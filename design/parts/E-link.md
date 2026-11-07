# RP2350 ↔ FPGA link — choice, signals, bandwidth and timing

> **ECP5 update (2026-11-07).** The link is unchanged on the RP2350 side (GPIO8–19, 8-bit PIO, 37.5 MHz, 37.5 MB/s; the bandwidth table below still holds). FPGA side, now all 3.3 V with no overdrive inputs and no series 100 Ω needed for clamp current: `LINK_D0–D7` → ECP5 bank-8 balls M7, N7, P7, R7, R6, T6, P8, M8 (configuration D2–D7, CS1N, DOUT; ordinary I/O once configured with CFG = 001); `LINK_IRQ` → M9 (WRITEN); `LINK_CLK` → M16 (PCLKT3_0); `LINK_DIR`, `LINK_STB` → R15, T15 (bank 3). Read round trip: RP2350 pad ≤ 4 ns (assumed) + 0.3 ns flight + ECP5 tCO ≤ 6.1 ns from the clock pin (DS-02012 Tab 3.22, −7) ≈ 10.4 ns. Sampling 3 sys cycles (20 ns) after CLK↓ leaves ≈ +9.6 ns. Writes: FPGA tSU ≥ 0, tH ≥ 3.0 ns (or tSU_DEL 1.33 / tH_DEL 0 with input delay) against 13.3 ns half-period → OK. The RP2350 still keeps the link pins Hi-Z until it has seen DONE (bank-8 D-pins have no pull during configuration). The Gowin pin numbers in the table below are superseded by `E-pinmap.md`.


Not a part; the interface decision architecture decision 3 left to block E. Sources: RP2350 datasheet (`datasheets/rp2350-lcsc.pdf`: PIO chapter, GPIO functions Tab 3, IO characteristics Tab 1436), GW1NR-9 DS117 Tab 3-19 (clock-tree delays), UG803 (pins), `E-fpga-gw1nr9.md`, `E-pinmap.md`.

## Choice: 8-bit parallel, PIO-driven, RP2350-clocked, half-duplex

| Option | Raw rate | Meets worst case (below)? | Pins | Notes |
|---|---|---|---|---|
| SPI, 1 bit, 37.5–50 MHz | 4.7–6.3 MB/s | no — below Ethernet RX line rate (12.4 MB/s) | 4 | |
| QSPI-style, 4 bit, 37.5 MHz | 18.75 MB/s | no (worst 30.9 MB/s); realistic case at 97 % | 7 | |
| QSPI-style, 4 bit, 75 MHz | 37.5 MB/s | on paper | 7 | 13.3 ns period: FPGA→RP read round trip ≈ 11 ns + RP input path leaves no margin without a returned clock |
| **8 bit parallel, 37.5 MHz (sys 150 MHz / 4)** | **37.5 MB/s** | **yes, 82 % worst, 49 % realistic** | **12** | read round trip fits in one 26.7 ns period (below) |

Chosen: **8-bit parallel**, with the RP2350's PIO as master (side-set clock), DMA on both ends, FIFOs in FPGA BSRAM.

## Signals (RP2350 GPIO → FPGA pin)

| Net | RP2350 | FPGA | Dir | Purpose |
|---|---|---|---|---|
| `LINK_D0…D7` | GPIO8–15 (pins 6–9, 11–14) | 76, 75, 74, 73, 72, 71, 70, 69 (bank 1, 3.3 V) | bidir | data; consecutive GPIOs for PIO `in`/`out` |
| `LINK_CLK` | GPIO16 (16) | 10 (GCLKT_6, bank 3, overdrive input, 100 Ω series) | RP → FPGA | transfer clock, 37.5 MHz |
| `LINK_DIR` | GPIO17 (17) | 79 (bank 3, OD input) | RP → FPGA | 0: RP2350 drives D; 1: FPGA drives D |
| `LINK_STB` | GPIO18 (18) | 80 (bank 3, OD input) | RP → FPGA | transaction framing (low = header follows) |
| `LINK_IRQ` | GPIO19 (19) | 68 (bank 1) | FPGA → RP | RX FIFO has a frame / audio block ready / fault |

Series 22 Ω at each driver on `LINK_D*` (both ends drive): rise ~1 ns, a 30 mm trace is 0.2 ns one way → just above tr/6, so source termination keeps edges clean. RP2350 drive set to 4 mA, slew slow.

Firmware rules: the RP2350 keeps GPIO8–18 Hi-Z (its reset state) until it has confirmed through JTAG that the FPGA is configured, because `LINK_CLK/DIR/STB` enter 1.8 V bank-3 pins in overdrive mode (`E-fpga-gw1nr9.md`). Turnaround: RP2350 releases D, toggles DIR, waits 2 clocks; the FPGA drives only while DIR = 1 and releases within 1 clock of DIR = 0.

## Bandwidth requirement (worst case, sustained)

| Stream | Direction | Rate | MB/s |
|---|---|---|---|
| Ethernet RX, line rate, 1518 B frames + 12 B link header (8 B PTP timestamp, length, status) per 1538 B wire time (frame + preamble/SFD 8 B + IFG 12 B) | FPGA → RP | 12.5 MB/s × 1530/1538 | 12.44 |
| (same with 64 B frames: (64 + 12)/84 × 12.5) | | | 11.31 |
| Ethernet TX, same bound | RP → FPGA | | 12.44 |
| Output audio: woofer, tweeter, HP/line L, R — 4 ch × 32 bit × 96 kHz (headroom over 48 kHz) | RP → FPGA | 12.29 Mbit/s | 1.54 |
| Mic audio: MEMS PDM (decimated in FPGA) + ext mic — 2 ch × 32 bit × 96 kHz | FPGA → RP | 6.14 Mbit/s | 0.77 |
| Sense/telemetry: 4 ch × 16 bit × 96 kHz (VBUS, I-sense, post-filter sense for DC detect / future closed loop) | FPGA → RP | 6.14 Mbit/s | 0.77 |
| Registers, status, PTP servo | both | | 0.10 |
| **Sum (half-duplex, both directions share the bus)** | | | **28.06** |
| + 10 % framing / turnaround (4 B header per transaction, 2-clock turnaround, ≥ 1 kB bursts) | | | **30.9** |

Capacity 8 bit × 37.5 MHz = **37.5 MB/s → 82 % at the worst case** (both directions at Ethernet line rate simultaneously, which a speaker never sees). Realistic: RX at line rate (broadcast storm or multicast audio flood) + TX ≤ 1 MB/s + audio/telemetry 3.1 MB/s → 16.5 MB/s × 1.1 = **18.2 MB/s = 49 %**.
Ordinary traffic (2–8 channels of AES67 at 48 kHz/24 bit ≈ 0.3–1.2 MB/s, PTP, control) is a few percent. The FPGA MAC filters by destination address and multicast group, so the RP2350 only receives frames it subscribed to; the line-rate case is a protection case, not a design point for the CPU.

## Timing

Period 26.67 ns (37.5 MHz). RP2350 → FPGA (writes): PIO changes D on CLK↓ (side-set), FPGA samples on CLK↑ → 13.3 ns setup minus skew (D and CLK leave the same PIO instruction; trace match ±5 mm = 33 ps) − 0.8 ns RC of the 100 Ω on CLK − FPGA input setup (≤ 1 ns assumed) → ≈ **+11 ns**. Hold ≈ 13 ns.
FPGA → RP2350 (reads): FPGA launches on CLK↓ as received. RP2350 pad out (assume ≤ 4 ns; not in Tab 1436) + flight 0.15 + series RC 0.8 + GCLK6–7 tree 2.5 ns (DS117 Tab 3-19, C6) + clock-to-pad ≤ 4.2 ns (pin-LUT-pin bound) + flight 0.15 ≈ **11.8 ns** after the RP2350's CLK↓. The PIO samples a fixed number of sys-clock cycles after it drives CLK↓; sampling 3 cycles (20 ns) later leaves ≈ +8 ns setup and ≥ +6.7 ns hold before the next launch (26.7 + min delay). The RP2350 input synchroniser (2 sys cycles) can be bypassed per pin (`INPUT_SYNC_BYPASS`) or folded into the sample offset; either way the window is deterministic. If bring-up shows less margin, run reads at sys/6 = 25 MHz (25 MB/s; still ≥ the realistic 18.2 MB/s).

## RP2350 resources

PIO: one state machine for the link (out 8 + in 8 + side-set CLK + DIR/STB via set pins), DMA channels for RX and TX ring buffers. 37.5 MB/s = 9.4 M 32-bit words/s, a small fraction of the bus fabric. HSTX (GPIO12–19) is overlapped by the link pins; it is not needed.
