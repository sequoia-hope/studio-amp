# U_CK1: SN74LVC2G34 dual buffer, MCLK_Q fan-out on +3V3_Q

Datasheet: `datasheets/sn74lvc2g34.pdf` (TI SN74LVC2G34). Read: features, pin functions, abs
max, recommended conditions, electrical and switching characteristics.
MPN: SN74LVC2G34DBVR. `C347589 SN74LVC2G34DBVR (TI, SOT-23-6): extended, JLC stock 38633, lifecycle normal, checked 2026-11-07`
Second source (alternate only; its Ioff is not verified, review n5): `C49365212 SN74LVC2G34DBVR-JSM (JSMSEMI, SOT-23-6L): extended, JLC stock 89480, lifecycle normal, checked 2026-11-07`
Footprint: SOT-23-6 (DBV).
Pins: 1 = 1A, 2 = GND, 3 = 2A, 4 = 2Y, 5 = VCC, 6 = 1Y.

## Why a buffer

Block E gives F one dedicated VCXO branch with a 33 Ω source resistor (`E-clk-audio-vcxo.md`).
The load to be driven is 8 FF CP inputs (4 pF each, 74LVC74A Table 7), plus PCM1808 SCKI, plus
traces: ≈ 32 + 5 + 10 = 47 pF. That is above the oscillator's 15 pF load class. The buffer
isolates the VCXO, so its own branch sees ≈ 3.5 pF (Ci) plus the trace.

## Connection

- VCXO branch to both 1A and 2A, tied, ≤ 10 mm.
- **1Y** → 22 Ω → the MCLK_Q daisy chain through the 4 × 74LVC74 CP pins (≈ 32 pF + trace).
- **2Y** → 33 Ω → PCM1808 SCKI. The ADC's input current spikes and its trace are kept off the
  DAC clock.
- VCC is **+3V3_Q**, with 100 nF at pin 5. The buffer's threshold noise follows its supply, which
  is why it must be on the quiet rail.

## Checks

| Item | Datasheet | Ours | OK |
|---|---|---|---|
| VCC | 1.65–5.5 V; abs max 6.5 V | 3.3 V | OK |
| Input transition | ≤ 10 ns/V at 3.3 V | VCXO edge ≤ 5 ns / 3.3 V = 1.5 ns/V | OK |
| Output drive | ±24 mA (VOH 2.3 V / VOL 0.55 V at 3.0 V) | 47 pF at 1 ns edges → ≈ 50 mA transient through 22 Ω, actually limited by the driver; average CV·f = 32 pF × 3.3 V × 24.576 MHz = 2.6 mA | OK |
| tpd | 1.4–4.1 ns (3.3 V ± 0.3 V, −40 to 85 °C) | a static delay common to all FFs | OK |
| TA | −40 to +125 °C | 55 °C | OK |
| +3V3_Q current | Cpd ~ 20 pF class × 3.3 V × 24.576 MHz ≈ 1.6 mA, plus the 2.6 mA load | **≈ 4 mA, which raises the +3V3_Q design load to ≈ 34 mA** | within the 50 mA LDO allowance |

**Jitter:** TI gives no additive-jitter figure for LVC gates. Single CMOS gates are commonly
characterised at ≈ 0.1–0.2 ps rms. Against the ≤ 1 ps budget that adds in quadrature (≤ 2 %).
This is an assumption, not a datasheet figure, so bring-up checks it by measuring the DAC noise
floor along with the VCXO.

## Layout

The buffer sits between the VCXO branch end and the first 74LVC74. 1Y runs along the four FF
packages with a ground reference underneath. Keep 2Y short to the PCM1808.
