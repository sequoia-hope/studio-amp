# RT (×4) — over-temperature NTCs: Murata NCP15XH103F03RC (10 kΩ ±1 %, B25/50 3380 K, 0402)

Datasheet: datasheets/ncp15xh103.pdf (Murata NCP series chip NTC thermistor catalogue). Read: part-numbering key, the NCP15 (0402) spec table, R–T table, notes on dissipation and land pattern.
MPN: NCP15XH103F03RC. Supplier: `C77131 NCP15XH103F03RC (muRata, 0402): extended, JLC stock 304962, lifecycle normal, checked 2026-11-07`.
Part key: NCP 15 (0402) · **XH** (nominal B-constant 3350–3399 K, i.e. 3380 K) · 103 (10 kΩ at 25 °C) · **F** (±1 %) · 03 · RC (paper tape) — datasheet numbering table.
Pull-ups: 10 kΩ 1 % 0402 (C25744) to 3V3_A; 100 nF 0402 at the ADC pin (C60474).

## Placement (feeds phase 6)
| NTC | Where | Measures |
|---|---|---|
| T_WOOF_FET | between the woofer channel's two legs, on the LS-source GND copper next to the FETs | board temperature at the FETs |
| T_WOOF_IND | between the woofer's two inductors | inductor and board temperature |
| T_TWT_FET, T_TWT_IND | same, tweeter channel | |

## Calculations
Divider: V = 3.3 V × R_NTC/(R_NTC + 10 k). R(T) = 10 k × exp[3380 × (1/T − 1/298.15)] (B-equation; the datasheet R–T table should be used in gateware for ≤ 0.5 °C accuracy):
| T | R_NTC | V | dV/dT |
|---|---|---|---|
| 25 °C | 10.0 k | 1.650 V | −31 mV/°C |
| 85 °C | 1.50 k | 0.430 V | −10 mV/°C |
| 100 °C | 1.02 k | 0.306 V | −7 mV/°C |
| 115 °C | 0.72 k | 0.221 V | −4.6 mV/°C |
Resolution at 110 °C: 0.806 mV/LSB ÷ 5.5 mV/°C ≈ 0.15 °C ✓.
Datasheet row for NCP15XH103F03RC: 10 kΩ ±1 %, B25/50 3380 K ±1 % (B25/80 3428, B25/85 3434, B25/100 3455 reference), **permissible operating current 0.31 mA**, rated power 100 mW, **typical dissipation constant 1 mW/°C**.
Current: 3.3 V/(10 k + R_NTC) = 0.165 mA at 25 °C, 0.31 mA at 115 °C (at the permissible limit only at the top of the range) ✓. Self-heating: at 25 °C P = 1.65²/10 k = 0.27 mW → 0.27 °C; at 115 °C 0.31² × 0.72 k = 0.07 mW → 0.07 °C ✓.

### Thresholds (gateware policy, block E; R-40, R-54)
- FET region: derate (limit power) at 95 °C board, shut down at 110 °C. Tj = T_board + P_FET × R_jb ≤ 110 + 0.63 W × 11.4 °C/W = **117 °C < 125 °C** (D-gan-fet.md).
- Inductor region: derate at 100 °C, shut down at 115 °C (SER2915H maximum part temperature 125 °C).
- The LMG1210's internal OTP (150 °C) is a backstop only.

## Fine print
- B tolerance ±1 % and R25 ±1 % → about ±1.5 °C near 100 °C. Gateware should use the B25/100 = 3455 K reference value (or the R–T table) above 85 °C, not 3380 K: at 110 °C the difference is ≈ 2 °C.
- Sensing lags: the NTC reads board copper, which follows the FET with a thermal time constant of seconds. That is acceptable because PoE limits sustained power (R-33a); burst heating is bounded by Tj at 144 W (≤ 108 °C even with no panel path).

## Open questions
None.
