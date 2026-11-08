# J (Qwiic) — buffered Qwiic I2C: SM04B connector, TCA9617B repeater, TPS2553 power switch (R-18)

Datasheets: datasheets/tca9617b.pdf (SCPS259F, Mar 2026, English, ti.com; LCSC's copy is the Chinese
translation), datasheets/tps2553.pdf (SLVS841E), datasheets/jst-sh-sm04b.pdf (JST SH catalogue
page), datasheets/srv05-4.pdf (Semtech).
Connector convention (Sequoia's boards): `JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal`, LCSC
C160404, **pin 1 GND, 2 +3V3, 3 SDA, 4 SCL** (StarlightEye; dancing_forest picks the supply with a
solder jumper). This is the SparkFun Qwiic order. No I2C buffer has been used on Sequoia's boards
before. Their I2C LED drivers (IS31FL3741A on motionhexa-matrix, simple_earring) are on-board, not
on Qwiic.

| Part | MPN | Supplier line |
|---|---|---|
| Connector | SM04B-SRSS-TB(LF)(SN) | `C160404 SM04B-SRSS-TB(LF)(SN) (JST, SMD,P=1mm,Surface Mount,Right Angle): extended, JLC stock 56332, lifecycle normal, checked 2026-11-07` |
| I2C repeater | TCA9617BDGKR | `C527429 TCA9617BDGKR (TI, VSSOP-8-0.65mm): extended, JLC stock 10628, lifecycle normal, checked 2026-11-07` |
| 3V3 power switch, 0.4 A limit | TPS2553DBVR | `C55266 TPS2553DBVR (TI, SOT-23-6): extended, JLC stock 57937, lifecycle normal, checked 2026-11-07` |
| ESD (SDA, SCL, rail) | SRV05-4.TCT | `C13612 SRV05-4.TCT (SEMTECH, SOT-23-6L): extended, JLC stock 66821, lifecycle normal, checked 2026-11-07` |

Alternatives: TCA4307 (hot-swap buffer with stuck-bus recovery) has only 80–100 in stock (fails the
stock rule's margin), PCA9515B (2281) is a plain repeater, and P82B715 needs a mate at the far end.
TCA9617B suits Qwiic: FM+ (1 MHz), B side drives 30 mA, each side up to 550 pF (description).

## Circuit

- Bus A (RP2350 side): VCCA = +3V3, SDAA/SCLA to RP2350 I2C, pull-ups 4.7 kΩ to +3V3 (unless
  block E already fits them on this bus).
- Bus B (cable side): VCCB = +3V3 (always powered, so the device isn't left half-powered when the
  cable power is off), SDAB/SCLB **direct** to J pins 3/4 (no series resistor, see gotchas). Pull-ups
  2.2 kΩ to `QWIIC_3V3` through a bridged solder jumper (cut to remove ours when the far boards bring
  enough).
- EN (revised after the 2nd review, MAJOR-1): **driven directly by `QWIIC_PWR_EN`, which now has a
  10 kΩ pull-down** (was 100 kΩ). The TCA9617B EN has an internal pull-up to VCCB:
  II(EN) = −25 µA at VI = 0.2 V (SCPS259F p. 6). Against 100 kΩ that left EN at ≈ 1.47 V with J16
  Hi-Z, above VIL(EN) = 0.3 × VCCB = 0.99 V. With 10 kΩ: EN ≤ 3.3 × 10/(10 + 124) ≈ 0.25 V (Thevenin
  of the internal pull-up ≈ 124 kΩ, from −25 µA at 0.2 V → (3.3 − 0.2)/25 µA). That is a valid low
  before configuration, with the FPGA unpowered, and with J16 Hi-Z. When J16 drives high it sources
  0.33 mA into the 10 kΩ (fine at 4 mA drive). The TPS2553 EN (VIH 1.1 V / VIL 0.66 V, no internal
  pull) sees the same net.
  Plus a **100 kΩ discharge from `QWIIC_3V3` to GND**: the TPS2553 has no output discharge, so this
  holds the B-side pull-ups at 0 V when off.
  Firmware notes: `QWIIC_PWR_EN` changes only with the I2C controller idle. After switching off, keep
  it low ≥ 3 s before re-enabling if the far end must see a defined 0 V first (τ = 100 kΩ × 10 µF = 1 s).
- Power: TPS2553 IN = +3V3, OUT = `QWIIC_3V3` → J pin 2, EN = `QWIIC_PWR_EN` (FPGA J16, **10 kΩ**
  pull-down: off at boot), FAULT_N → `QWIIC_FAULT_N` (10 kΩ to +3V3), RILIM **150 kΩ** 1 % (user cap 100 mA, 2026-11-07). 1 µF on IN,
  10 µF on OUT.
- ESD: SRV05-4 at the connector: I/O lines on SDA and SCL, pin 5 (VCC rail) = `QWIIC_3V3`, pin 2 GND.

## Absolute max vs our worst case

| Parameter | Abs max | Ours | Margin |
|---|---|---|---|
| TCA9617B VCCA, VCCB, I/O | −0.5…7 V | 3.3 V; I/O 3.3 V (5 V tolerant) | OK |
| TCA9617B IOL (ROC) | 30 mA | (3.3 − 0.5)/1.1 kΩ = 2.5 mA | OK |
| TPS2553 IN/OUT/EN/FAULT | −0.3…7 V | 3.3 V | OK |
| TPS2553 IOUT (ROC) | 1.2 A (TJ ≤ 125 °C) | ≤ 0.207 A limit | OK |
| JST SH contact | 1.0 A (AWG 28), 50 V | 0.207 A worst | 4.8× |
| SRV05-4 VRWM | 5 V | 3.3 V | OK |

## Calculations

**Current limit** (revised 2026-11-07: **the user capped Qwiic power at 100 mA in firmware**). TPS2553
eq. 1, RILIM in kΩ: RILIM = **150 kΩ** (inside 15–232 kΩ) → IOS min 25230/150^1.016 = **155 mA**, nom
23950/150^0.977 = **179 mA**, max 22980/150^0.94 = **207 mA**. That is above the 100 mA firmware cap
(≥ 55 % margin for inrush into downstream boards' caps; soft start limits it anyway) and far below the
SH contact rating. Loss at 100 mA: 0.1² × 0.135 = 1.4 mW. (Superseded: 64.9 kΩ, 364–455 mA, for the
300 mA R-18 allowance.)

**Pull-ups / bus capacitance** (TCA9617B §8.2.1.2.1; I2C rise time 0.8473·R·C):
- Ours 2.2 kΩ, typically in parallel with one SparkFun board's 2.2 kΩ → 1.1 kΩ.
- tr = 0.8473 × 1.1 kΩ × C: 93 ns at 100 pF, 186 ns at 200 pF, 373 ns at 400 pF, 513 ns at 550 pF.
  Fast mode (300 ns) holds up to ≈ 320 pF (≈ 1–2 m of Qwiic cable plus a few boards). Beyond that,
  run at 100 kHz (1000 ns) up to the 550 pF limit.
- Minimum total pull-up: every B-side device must pull below VILB = 0.4 V. A standard-mode device
  guarantees VOL ≤ 0.4 V at 3 mA → Rp,total ≥ (3.3 − 0.4)/3 mA = 967 Ω. With ours plus one 2.2 k board
  (1.1 kΩ) this is met. With more pulled-up boards on the chain, cut our jumper.
- Rise time ≥ 20 ns on B (§8.2.1.2.1, limits pedestal overshoot): at 1.1 kΩ this needs C ≥ 21 pF.
  The connector, ESD (3 pF) and cable always exceed that.
- ESD capacitance: SRV05-4 is 3 pF typ / 5 pF max per line, negligible against the bus budget. The
  PESD5V0S1BL (35 pF) was rejected here for that reason.

## Fine print / gotchas

- **B-side static offset**: TCA9617B drives the B side to VOLB = 0.48–0.58 V, not 0 V (EC). B-side
  targets see 0.53 V as low (VIL 0.3 × 3.3 = 0.99 V), but **a second offset-type buffer on the cable
  side (e.g. another TCA9617/PCA9515 on the LED driver board) would not be recognised**. Rule for
  Qwiic accessories: no static-offset repeater on the far end.
- **No series resistor on SDAB/SCLB**: a remote device's 0.4 V low plus I·R across a series resistor
  (2.5 mA × 47 Ω = 0.12 V) would exceed VILB = 0.4 V, and the repeater would miss the low. R-42's
  "series resistors" rule is waived on this port for that reason. ESD is handled by the SRV05-4 plus
  the TCA9617B's ±4 kV HBM.
- EN must change only when both buses are idle (§7.4). Firmware switches `QWIIC_PWR_EN` only with
  the I2C controller idle. EN follows cable power, so this is the same rule.
- VCCA ≤ VCCB required (§8.2.1.1): both are +3V3. OK.
- Addresses: the repeater is transparent, so Qwiic accessories share the address space of the
  RP2350's I2C bus. Block E dropped its TCA9535 (0x20) after the ECP5 switch, so no address is
  reserved now. Recheck if block E puts any device on this bus.
- On USB-only power, keep `QWIIC_PWR_EN` low unless the port is known to supply > 500 mA
  (C-5v-mux.md).

## Layout guidance

- SRV05-4 right at J's pins, GND pin with its own via. TCA9617B decoupling 100 nF on each VCC pin.
- RILIM at the TPS2553 ILIM pin (datasheet: keep RILIM traces short).

## Open questions

- Confirm with block E that the RP2350 I2C bus already has (or doesn't have) A-side pull-ups.
- Confirm the LED-driver board's I2C pull-up value so the jumper default can be decided.
