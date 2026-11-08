# Block C — power-good chaining and sequencing (R-23, R-34)

No new ICs: this file collects how the block C parts' enables and power-good outputs combine, so the
schematic and firmware implement one scheme. Sources: the per-part audits and their datasheets.

## Hardware chain

```
VBUS rises (ACF soft start, block B)
 │
 ├─ ≥ 36.2 V: LM5013 EN/UVLO → 3.5 ms soft start → +5V_BUCK
 │     └─ PGOOD (FB ≥ 95 %) → PG_5V = 3.24 V
 │           └─ TPS2116 PR1 high → +5V from the buck (USB released, RCB both ways)
 │                 ├─ TPS62A02AP (3V3), EN = +5V → ≤ 1 ms → +3V3 → PG_3V3
 │                 │     ├─ TPS7A9401 (2V5), EN_UV = PG_3V3 → ≈ 1.2 ms → +2V5
 │                 │     └─ TPS62A02AP (1V1), EN = PG_3V3 → ≤ 1 ms → +1V1  (ECP5: 3V3 first, then 1V1/2V5 within ≈ 1 ms)
 │                 └─ TPS7A9401 (3V3_Q), IN = +5V, EN_UV = +15V ÷ 5.7 (on at +15V ≥ 7.1 V)
 ├─ ≥ 35.9 V: LM5017 Fly-Buck UVLO → +18.4 / −17.8 V → TPS7A49/30 (14 ms NR soft start) → ±15 V
 │     └─ +15V → TPS7A4901 → +5V_A; +15V enables 3V3_Q
 └─ LM5017 VDRV: **off** until VDRV_EN (firmware) → VDRV 7.04 V → TLV6703 → VDRV_PG

USB only (no VBUS): PG_5V = 0 → TPS2116 takes VUSB → +5V → +3V3, +2V5, +1V1, +3V3_A.
VDRV, ±15 V, +5V_A, +3V3_Q and +5V_LED stay off. There is no VBUS, so neither LM5013 nor either LM5017 runs. R-23 met.
```

## Firmware/FPGA conditions before the amplifier unmutes (R-34)

RP2350 boot (after +3V3):
1. Load the FPGA bitstream over SSPI, then wait for the FPGA's DONE (block E).
2. Check `PD_PG_N` **low** (= PD power good; isolated, active low, block A), `POE_LOSS_N` **high**
   (= no pulse loss; open drain, active low, block B), `PG_5V_N` **low** (= 5 V buck good; buffered
   copy, active low), and VBUS_SENSE within 44–55 V (block D ADC).
3. Assert `VDRV_EN`. Wait ≥ 1 ms (TLV6703 needs 150 µs of valid VDD, plus LM5017 start-up), then
   require `VDRV_PG` high.
4. Tell the FPGA to start PWM at zero modulation and ramp the volume (block D/E: pop-free start).

The FPGA keeps a hardware gate in its fabric: PWM is held off (all LI/HI low) unless
`VDRV_PG_ok & !PD_PG_N & POE_LOSS_N & !fault` is true (VDRV_PG reaches the FPGA over the RP2350 link,
per block D), independent of firmware. On PoE loss (R-32a: `PD_PG_N` goes **high**, or block B's
`POE_LOSS_N` goes **low**, whichever comes first), the FPGA ramps the output to zero in ≤ 5 ms, then stops switching. After that,
firmware de-asserts `VDRV_EN`.

Hardware backstops while the FPGA is unconfigured. **ECP5 GPIO default to tristate with weak
pull-downs of 30–150 µA** (TN-02039 §5, TN-02038 Table 9.1). The rule after the phase 1 review (B1/B2):
**no power-control or strapping node may be loaded by an unconfigured ECP5 pin.** See the sweep table
in C-interfaces.md, "Review response". Other backstops:
- VDRV is off (VDRV_EN has a 100 kΩ pull-down), so the drivers have no supply.
- Block D (D-interfaces.md): each channel's LMG1210 EN comes from a 74LVC1G74 latch whose CLR is held
  low by a 10 kΩ pull-down on the FPGA's AMP_ARM, so EN = 0 until the configured FPGA drives ARM high.
  The PWM lines also get 4.7 kΩ pull-downs (below the 0.7 V VIF min against 150 µA). Gateware waits
  ≥ 200 µs after VDRV_PG (LMG1210 tSTLS ≤ 150 µs) before arming.

## Shutdown / hold-up

- VBUS decay from 48 V to the LM5013 UVLO-off point (33.8 V, 32.6–35.5 V spread) on 5 mF at 8 W
  logic + gate + analog: 0.36 s. On 1 mF: 73 ms. Both exceed R-34's 20 ms.
- The Fly-Buck UVLO falls at 33.4 V, about the same time, so ±15 V ramps down after the amp is long
  muted.
- +5V collapses only when PG_5V falls (buck < 90 % of setpoint). The mux would then select VUSB if
  present, which gives seamless bench operation with USB plugged in.

## Timing summary (typical)

| Event | t after VBUS crosses 36 V |
|---|---|
| +5V_BUCK in regulation, PG_5V | ≈ 3.5 ms |
| +3V3 up, PG_3V3 | ≈ 4.5 ms |
| +1V1 up | ≈ 5.5 ms |
| +2V5 up (TPS7A94: fast charge to ≈ 93 %, then 150 µA, review) | ≈ 6.8 ms |
| +3V3_Q up (CNR 4.7 µF: 6.9 + 7.2 ms, then the 1.5 Hz NR filter settles) | ≈ 14 ms after +15V ≥ 7.1 V |
| ±15 V up | ≈ 15 ms |
| RP2350 boot + FPGA load (block E) | tens to hundreds of ms |
| VDRV_EN → VDRV_PG | ≤ 1 ms after firmware asserts it |

## Isolation links for bring-up (R-80)

Bridged solder jumpers (cut to isolate), or 0 Ω where the current exceeds a jumper's copper:
- VBUS → LM5013 VIN; VBUS → VDRV LM5017 VIN; VBUS → Fly-Buck VIN (0 Ω 1206 or 2 mm bridged copper).
- +5V_BUCK → TPS2553 (LED); +5V_BUCK → TPS2116 VIN1.
- +5V → 3V3 buck; +5V → 1V1 buck; +3V3 → 2V5 LDO; +5V → 3V3_A; +5V → 3V3_Q.
- VDRV → each LMG1210 (4 links, block D side).
- +15V / −15V LDO outputs → block F.
A test point sits on each side of every link (see G-testpoints.md).

## Note: TPS2116 start-up blip on PoE-only power (review note)

While +5V_BUCK ramps from 0 to ≈ 1 V, MODE (tied to VIN1) is still low and PR1 low, so the TPS2116
passes the higher input and +5V follows the buck up to ≈ 1 V. When MODE crosses its 1 V threshold
with PR1 still low, VIN2 (absent) is selected and +5V collapses until PG_5V asserts ≈ 3.5 ms later.
This is harmless (the TPS62A02A UVLO is ≈ 2.4 V) but visible on a scope at bring-up. It is expected,
not a fault.
