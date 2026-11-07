# U_DAC1–U_DAC4: 74LVC74A dual D flip-flop, the 1-bit DAC reclock

Datasheet: `datasheets/74lvc74.pdf` (Nexperia 74LVC74A, Rev. 11, 22 Feb 2024). Read in full: pinning,
limiting values, recommended conditions, static and dynamic characteristics, test circuit and
package.
MPN: 74LVC74APW,118 (Nexperia)  Supplier: `C6100 74LVC74APW,118 (Nexperia, TSSOP-14): extended, JLC stock 2161, lifecycle normal, checked 2026-11-07`
Second source (pin-compatible, same TSSOP-14): `C350561 SN74LVC74APWR (TI, TSSOP-14): extended, JLC stock 1278, lifecycle normal, checked 2026-11-07`
Quantity: 4 per board (4 taps × 2 channels = 8 flip-flops), so 20 for 5 boards, 24 with attrition.
Single-tap build: 1 per board.
Footprint: TSSOP-14, 4.4 mm body, 0.65 mm pitch (SOT402-1, matches the "PW" suffix; datasheet p.1
ordering table).

Why LVC rather than AHC: LVC74A has the stronger and more symmetric output drive (VOL 0.55 V at
24 mA; VOH 2.2 V at −24 mA at 3.0 V), tpd of 2.6 ns typ, and Schmitt-trigger inputs on every pin,
CP included. The hysteresis on CP reduces how much noise on the clock edge turns into jitter. Both
LVC and AHC have 5 V-tolerant inputs.

## Absolute max vs our worst case

| Parameter | Abs max (Table 5) | Our worst case | Margin |
|---|---|---|---|
| VCC | −0.5 to 6.5 V | 3.3 V ± 3 % (3V3_Q LDO) | OK |
| VI | −0.5 to 6.5 V | 0–3.3 V (FPGA LVCMOS33, MCLK buffer) | OK |
| IO | ±50 mA | 1.5 mA DC per output (2.2 kΩ to the ≈ 1.3 V node), plus the C0 charging peak of (3.3 V − 1.3 V)/2.2 kΩ ≈ 0.9 mA (C0 is behind R0) | OK |
| Ptot | 500 mW (TSSOP derates 7.3 mW/K above 81 °C) | ≈ 30 mW per package | OK |
| Tamb | −40 to +125 °C | 55 °C | OK |

## Recommended operating conditions (Table 6)

- VCC 1.65–3.6 V for maximum speed: 3.3 V. OK.
- Input transition rate ≤ 10 ns/V at 2.7–3.6 V. The XO/buffer edge on CP is ~1–2 ns per 3.3 V,
  and the FPGA DAC_x outputs are likewise fast. OK. **The MCLK_Q trace must not be RC-filtered.**

## Required external parts

- 100 nF X7R 0402/0603 from VCC (pin 14) to GND (pin 7) at each package, plus one 10 µF X7R per
  group of four packages at the `+3V3_Q` entry point (the low supply impedance is the THD
  requirement, see Calculations).
- nSD and nRD (pins 1, 4, 10, 13): tie high to `+3V3_Q`. Each FF's nRD can optionally go through
  10 kΩ to an FPGA "DAC_RESET_N" to force a known state at start-up. Not used: the FPGA streams
  the idle pattern before the relays close.
- Series resistor of 33 Ω at the FPGA end of each DAC_x line (edge-rate and ringing control).
  The value is checked in phase 8 SI.

## Pin use

1RD(1), 1D(2), 1CP(3), 1SD(4), 1Q(5), 1Q̄(6), GND(7), 2Q̄(8), 2Q(9), 2SD(10), 2CP(11), 2D(12),
2RD(13), VCC(14) (Table 2). One package holds taps k and k+1 of one channel, so all four of a
channel's taps sit in two adjacent packages.

## Calculations

**Timing at MCLK = 24.576 MHz (T = 40.69 ns), 3.0–3.6 V, −40 to +85 °C (Table 8):**
- fmax ≥ 150 MHz: OK.
- tsu = 2.0 ns min, th = 1.0 ns min. The FPGA launches on the MCLK falling edge, so data arrives
  T/2 − (FPGA clock insertion + tco + flight) before the capturing rising edge. With FPGA
  tco + insertion ≤ 12 ns (block E to confirm), the setup slack is 20.3 − 12 − 2.0 = 6.3 ns. The
  hold slack is ≥ 20 ns. OK.
- tpd CP→Q: 1.0–5.2 ns. Only its variation matters (jitter). Its static value is a common delay.

**Output resistance (Table 7, at VCC = 3.0 V):**
- High side: (3.0 − 2.4 V)/18 mA ≤ 33 Ω.
- Low side: 0.55 V/24 mA ≤ 23 Ω.

Against R0 = 2.2 kΩ per tap, that is ≤ 1.5 %. Each state has a fixed resistance, so the error is a
fixed gain/offset per state (the 1-bit DAC stays two-level and linear). The H/L asymmetry appears
only as a DC offset, which the servo removes.

**Why differential Q/Q̄ cancels rise/fall ISI:** Let Q rise with area deficit A_r = VDD·tr/2 and
fall with area excess A_f = VDD·tf/2, and let Q̄ do the reverse.
- Up transition of (Q − Q̄): error −(A_r + A_f).
- Down transition: error +(A_f + A_r).

Up and down transitions alternate, so the error sequence is the derivative of the bit stream
times a constant. That is a fixed delay of (tr + tf)/2: linear. A single-ended output instead
leaves (A_f − A_r) per transition pair, which depends on the transition density and so on the
signal. The residual in the differential case is the Q/Q̄ mismatch (second order).

**Supply current on +3V3_Q (Table 8 note 4: PD = CPD·VCC²·fi·N + ΣCL·VCC²·fo):**
- Clock: CPD = 19.1 pF per FF at 3.3 V, fi = 24.576 MHz, so I = 19.1 pF × 3.3 V × 24.576 MHz =
  1.55 mA per FF, 12.4 mA for 8 FFs. This part is data-independent.
- Output load: whichever of Q/Q̄ is high sources (3.3 − 1.3 V)/2.2 kΩ = 0.91 mA. Exactly one is
  high per FF, so 7.3 mA for 8 FFs.
- Output capacitance: ≈ 10 pF trace + pad. ΣCL·VCC·fo ≈ 10 pF × 3.3 V × 3 MHz ≈ 0.1 mA per output.
- **Total ≈ 20 mA typ, 30 mA design.** Single-tap build: 2 FFs × (1.55 + 0.91 × 4) ≈ 7 mA (the
  560 Ω tap draws 3.6 mA).

**Data-dependent supply current and THD:** The tap-high current depends on the filter input node
voltages P±, which carry the signal. The average I_DD = const − a·x²/R0, where a·x is the P-node
signal. At full scale (a·x ≈ 0.41 V, R0 = 550 Ω equivalent) this is ΔI ≈ 0.37 mA at 2f. With
Zout(+3V3_Q) ≤ 0.1 Ω, ΔVDD ≤ 37 µV. That modulates the output by x·ΔVDD/VDD, so H3 ≈ −120 dB re
full scale. **Requirement for block C: Zout ≤ 0.1 Ω from 20 Hz to 50 kHz.**

**+3V3_Q noise:** The output is ∝ VDD·m. At 1 Vrms (m = 0.125) the output noise from VDD is
3.51 × 0.125 × δVDD = 0.44·δVDD. Keeping that ≤ 2 µV needs δVDD ≤ 4.6 µVrms
(20 Hz–20 kHz). **Requirement: ≤ 5 µVrms.** At idle the VDD noise is common-mode and is rejected
by the resistor match.

## Fine print / gotchas

- Table 8 note [3]: tsk(o) ≤ 1.0 ns between outputs switching in the **same** direction. Q and Q̄
  switch in opposite directions, which is not specified. Their skew is a fixed delay, linear to
  first order. Phase 8 models a skew of up to 1 ns.
- DHVQFN-14: the centre pad is "not a ground pin". Not used, since TSSOP was chosen.
- Do not feed CP through FPGA fabric or a PLL (jitter; see `F-overview.md`).
- ESD HBM 2 kV. The FF is not externally reachable (it sits behind the filter and relays).

## Layout guidance

- Put all four packages in a row along one edge of the filter, with the 100 nF caps right at
  pin 14. `+3V3_Q` arrives as a short pour from the LDO, with no other loads on it.
- Route MCLK_Q as a single daisy-chain or star with a source series resistor, kept short and away
  from the FPGA's other I/O and the GaN stage. Give it a ground reference with no plane split
  under it.
- Q/Q̄ to the 2.2 kΩ tap resistors: equal lengths, ≤ 10 mm. The resistors sit at the FF pins, with
  the P± summing nodes and C0 at the filter.

## Power sequencing (added after block C's update)

+3V3_Q is now gated by +15 V and is off on USB-only power, while the FPGA (+3V3) is up. This
datasheet gives the inputs as 5 V-tolerant (VI up to 6.5 V regardless of VCC), but specifies no
Ioff. So the gateware holds every DAC_x line low until 3V3_Q is good (PG_3V3Q), and the clock
reaches the FFs only through the Ioff-rated SN74LVC2G34. Layout: the TPS7A9401's SNS is a Kelvin
trace to this package row's VCC.

## Open questions

- Block E confirms that 8 DAC pins are available. If not, fit the single-tap option, which
  tightens the jitter requirement to ≤ 0.3 ps.
