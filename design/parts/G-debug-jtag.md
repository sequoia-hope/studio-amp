# J (SWD), J (UART), J (JTAG) — RP2350 debug-probe headers and FPGA JTAG (R-21, R-22)

Datasheets: datasheets/fg-1.0-3pwt.pdf (FG 1.0 mm horizontal SMD header drawing, viewed as an
image), datasheets/jst-sh-sm04b.pdf (JST SH series catalogue, for the mating SHR housing),
datasheets/xfcn-pz254v-11.pdf (1×6 2.54 mm header), datasheets/srv05-4.pdf,
datasheets/pesd5v0s1bl.pdf, datasheets/lattice-FPGA-TN-02038.pdf (ECP5 hardware checklist,
JTAG pull resistors) and datasheets/lattice-FPGA-TN-02039.pdf (sysCONFIG). The FPGA is now an ECP5
LFE5U-25F; the Gowin UG290 notes no longer apply.

## Convention from Sequoia's boards (Raspberry Pi Debug Probe, 3-pin JST SH)

From `~/pcb/rp2350-motor-controller/hardware/rp2350_driver.kicad_sch`, `~/pcb/rp2350-bike-light` and
`~/pcb/comms/hardware/comms/01_mcu.kicad_sch`:
- Footprint `Connector_JST:JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal`; the mounting pads go
  to GND.
- **SWD: 1 = SWCLK, 2 = GND, 3 = SWDIO.**
- **UART: 1 = RX (target receive, `RXI_DEBUG`), 2 = GND, 3 = TX (target transmit, `TXO_DEBUG`)**,
  with 100 Ω series resistors on both (bike-light).
- LCSC: the genuine JST part C160403 now has **0 stock**. rp2350-motor-controller uses the FG
  clone C2763613 on the same KiCad footprint, so this board does too.

| Part | MPN | Supplier line |
|---|---|---|
| SWD and UART headers ×2 | FG 1.0-3PWT (JST SM03B-SRSS-TB compatible) | `C2763613 1.0-3PWT (FG, SMD,P=1mm,Surface Mount,Right Angle): extended, JLC stock 11360, lifecycle normal, checked 2026-11-07` |
| (genuine JST, unavailable) | SM03B-SRSS-TB(LF)(SN) | `C160403 SM03B-SRSS-TB(LF)(SN) (JST, SMD,P=1mm,Surface Mount,Right Angle): extended, JLC stock 0, lifecycle normal, checked 2026-11-07  <-- CHECK` |
| FPGA JTAG 1×6 2.54 mm (optional population) | PZ254V-11-06P | `C492405 PZ254V-11-06P (XFCN, Through Hole,P=2.54mm): extended, JLC stock 97177, lifecycle normal, checked 2026-11-07` |
| ESD (SWD + UART: 4 lines) | PESD5V0S1BL,315 ×4 | `C84374 PESD5V0S1BL,315 (Nexperia, DFN1006-2): extended, JLC stock 76124, lifecycle normal, checked 2026-11-07` |
| ESD (JTAG: 4 lines, rail +3V3) | SRV05-4.TCT | `C13612 SRV05-4.TCT (SEMTECH, SOT-23-6L): extended, JLC stock 66821, lifecycle normal, checked 2026-11-07` |

FG 1.0-3PWT drawing (checked by eye): 1.0 mm pitch, signal pads 0.6 mm wide, mounting pads
1.2 × 1.8 mm, contact resistance ≤ 30 mΩ, withstand 500 VAC, −20…+85 °C. Mates with JST SHR-03V-S
housings, which the Debug Probe cables use. **Phase 2: overlay the FG pad drawing on the KiCad
SM03B footprint and confirm the pad row-to-MP distance (5.55 / 4.0 mm on the FG drawing).**

## Circuits

- **SWD**: SWCLK and SWDIO from the RP2350 through 33 Ω each, PESD5V0S1BL at the header. 33 Ω ×
  35 pF = 1.2 ns, harmless at SWD's ≤ 10–24 MHz. Whether SWCLK/SWDIO need external pulls
  is block E's call (RP2350 datasheet, SWD section); none are fitted here.
- **UART**: RP2350 UART0 TX → 100 Ω → pin 3; pin 1 → 100 Ω → RP2350 UART0 RX (Sequoia's
  convention). PESD5V0S1BL on each. At 115.2 kbaud to 3 Mbaud this is trivial.
- **FPGA JTAG** (proposed pinout, 1×6 2.54 mm): 1 = +3V3 (VREF), 2 = GND, 3 = TCK, 4 = TDO, 5 = TDI,
  6 = TMS. Series 33 Ω on all four signals, SRV05-4 at the header (pin 5 → +3V3).
  - **ECP5 revision (2026-11-07)**: the header connects directly to the ECP5's dedicated JTAG pins
    (bank 8, 3.3 V). Per the ECP5 hardware checklist (datasheets/lattice-FPGA-TN-02038.pdf, JTAG
    table): **TDI, TMS, TDO 4.7 kΩ pull-up to VCCIO8; TCK 4.7 kΩ pull-down to GND.**  **Block E fits them on its sheet at the FPGA**
    (E-interfaces.md); block G does **not** fit a second set at the header. VREF (pin 1) = VCCIO8 = +3V3.
  - TN-02039 (sysCONFIG) notes that TCK has no internal pull-up and recommends the external 4.7 kΩ
    pull-down "to avoid inadvertently clocking" the TAP.
  - Signal integrity: 33 Ω × (SRV05-4 3 pF + ≈ 10 pF) τ < 1 ns, fine for the ≤ 25–30 MHz typical of
    ECP5 JTAG cables.
  - Usable with openFPGALoader and any 3.3 V JTAG cable (FT2232/FT232H, CMSIS-DAP). The RP2350 could
    also drive these pins itself if block E routes them (not proposed: the RP2350 configures over
    SSPI).

## Calculations / checks

- JST SH contacts 1 A, 50 V (JST catalogue). The signals carry µA–mA. OK.
- ESD: R-42 asks inward headers for series R and light TVS. PESD5V0S1BL: VRWM 5 V, VBR 5.5–9.5 V,
  clamp 14 V, IEC 61000-4-2 level 4, 35 pF. With 33–100 Ω series it keeps the RP2350 pins within
  their injection limits during an 8 kV contact discharge (current shared with the internal diodes).

## Open questions

- User: is the FPGA JTAG pinout above the one your programmer cable uses (an FT2232H/Tigard-style 6-pin, the Lattice HW-USBN-2B 1×8/2×5, or a
  2×5 1.27 mm ARM-style)? A 1×6 0.1 in header is assumed.

## Phase 2: FG 1.0-3PWT land pattern check (2026-11-07)

Read from the rendered drawing (datasheets/fg-1.0-3pwt.pdf, "PCB LAYOUT"; A = 2.00 mm for 3 pins):
signal pads 0.60 × 1.55 mm (5.55 − 4.0) at 1.00 mm pitch; MP pads 1.20 × 1.80 mm, inner edge
0.70 mm from the pin-1 centre (MP centres ±2.30 mm); 5.55 mm from the MP bottom edge to the signal-pad top
edge. KiCad `JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal` has signal pads 0.6 × 1.55 at
y −2.0, MP 1.2 × 1.8 at (±2.3, 1.875): the same pattern, so the KiCad footprint is kept for C2763613.
