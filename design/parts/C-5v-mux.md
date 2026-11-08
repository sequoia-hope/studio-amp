# U (5V mux) — TPS2116 priority power mux: +5V_BUCK / VUSB → +5V (R-23)

Datasheet: datasheets/tps2116.pdf (SLVSFG1A, May 2021, English, from ti.com; LCSC's copy is the
Chinese translation ZHCSN31A). Read: all sections.
MPN: TPS2116DRLR   Supplier: `C3235557 TPS2116DRLR (TI, SOT-583): extended, JLC stock 53288, lifecycle normal, checked 2026-11-07`
Footprint: SOT-583 "DRL" 8-pin (2.1 × 1.6 mm). Pins (Table 5-1, p.3): 1 GND, 2 and 7 VOUT (tie
both), 3 VIN1, 4 PR1, 5 MODE, 6 VIN2, 8 ST.

Rejected alternative: 2 × LM66100 (datasheets/lm66100.pdf, C2869734, 7347 stock), the "two ideal
diodes" R-23 names. Per its §9.2.1, two LM66100s with cross-coupled CE pass the higher input, but
§9.2.2 warns that "when both input voltages are the same for a long period of time, then both devices
will completely turn off". A 5.05 V buck and a 5.0 V USB port are the same voltage. The §9.2.2 fix
(ST-driven switchover) also still lets USB carry the load whenever it is higher, which would load a
500 mA PC port with ≈ 0.55 A of logic. LM66100 is also only 1.5 A.

## Absolute max vs our worst case

| Parameter | Abs max (§6.1) | Our worst case | Margin |
|---|---|---|---|
| VIN1, VIN2 | −0.3…6 V | +5V_BUCK 5.12 V max; VUSB 5.25 V (USB 2.0), ESD clamped by SMF5.0A (G-usb-c) | OK static; ESD clamp 9.2 V at 21.7 A exceeds 6 V for ns (see gotchas) |
| PR1, MODE, ST | 6 V | PR1 = PG_5V 3.24 V; MODE = VIN1 | OK |
| IOUT continuous (ROC) | 2.5 A | 0.55 A typ, < 1 A worst | OK |
| RON | 40 mΩ typ | P = 0.55² × 0.06 = 18 mW | OK |

## Required external parts / configuration

- **Priority mode**: MODE tied to VIN1 (§7.6.1). VIN1 = `+5V_BUCK`, VIN2 = `VUSB`.
- **PR1 = `PG_5V`** (the LM5013 PGOOD node, 3.24 V high / 0 V low; see C-5v-buck.md) in place of
  the datasheet's VIN1 divider. PR1 > VREF (0.92–1.08 V) selects the buck. PR1 low selects USB if
  present, otherwise nothing. This means +5V appears from the PoE side only once the buck is in
  regulation, and switches to USB if the buck drops out of regulation.
- CIN ≈ 1 µF on each input (§9): 1 µF on VIN1 (the buck's 3 × 22 µF are adjacent anyway). On VIN2,
  4.7 µF total including the connector side, which keeps the USB-C sink within the 10 µF attach limit.
- COUT: §7.3.4 recommends ≈ 100 µF if reverse-current blocking is expected. It is, on every
  switchover. Use 2 × 47 µF 10 V X5R 1206 (CL31A476MPHNNNE, basic) plus the downstream bucks' 4.7 µF
  inputs. Assume ~40 % retained at 5 V (to be confirmed on the curve) → ≈ 40 µF; acceptable, the
  bucks' input caps add more.
  `C96123 CL31A476MPHNNNE (Samsung Electro-Mechanics, 1206): basic, JLC stock 456950, lifecycle normal, checked 2026-11-07`
- ST: open drain, low when VIN2 is in use. Pull it up with 100 kΩ to +3V3 as `PWR_FROM_POE`, an
  optional RP2350 input that tells firmware whether it is on USB power. §7.3.3 says it "should be
  pulled up … for proper operation", so fit the pull-up even if the GPIO isn't used.

## Calculations

- Switchover dip (§7.6.1, break-before-make): tSW = 8 µs at 5 V (RL 10 Ω, CL 10 µF). With 0.55 A
  and ≥ 40 µF effective: ΔV = 0.55 × 8 µs / 40 µF = 0.11 V. +5V stays above 4.8 V; the TPS62A02As
  (2.5 V min) and TPS7A20 don't notice.
- Soft start (§7.3.2, eq. 1) applies only from VOUT < 1 V: the 1.3 ms typical ramp into ≈ 100 µF
  gives I = 100 µF × 5 V / 1.7 ms = 0.29 A inrush. That is within USB's budget when starting from USB.
- USB-only load (revised for ECP5): 3V3 at block E's 350 mA + display 40 + block D 85 + 2V5 50 mA =
  0.53 A → 1.94 W, plus 1V1 0.54 W and 3V3_A 0.08 W → 0.51 A at 5 V. That is at the 500 mA USB 2.0
  limit with block E at its design load. In USB-only mode firmware holds the PHY in reset (−90 mA on
  3V3) and keeps LEDs and Qwiic off (block E). Block E's typical share is ≈ 0.9 W, so the USB draw is
  ≈ 0.3 A typical and ≈ 0.45 A at design load (block D at 85 mA), inside 500 mA but with only 10 % margin. 3V3_Q, ±15 V, relays and LEDs are off on USB. With Qwiic loaded to
  300 mA, add 0.22 A → 0.61 A, over a 500 mA USB 2.0 port, so **on USB power firmware keeps Qwiic
  power off** (`QWIIC_PWR_EN`) unless VUSB_DET/CC shows a stronger source. Block E's typical
  185 mA gives ≈ 0.25 A from USB.

## Fine print / gotchas

- §7.4 VINx collapse rate: if the powering supply falls faster than 1 V/10 µs, the other must be
  ≥ 2.5 V or the device resets and restarts with soft start. On PoE loss the buck output falls slowly
  (VBUS bulk), so this doesn't apply.
- RCB (§7.3.4) trips at VOUT > VIN + 42 mV and releases at 17 mV. It is always active, so USB can
  never back-feed `+5V_BUCK` and the LEDs.
- ESD on VUSB: the SMF5.0A clamps to 9.2 V at 21.7 A (8/20 µs). An 8 kV contact discharge into the
  connector shell or VBUS can briefly exceed the 6 V abs max at VIN2. The TVS sits at the connector
  and the mux is behind ≥ 10 mm of trace, plus the USBLC6 VBUS clamp (VBR ≥ 6 V). This is accepted
  residual risk for the bring-up port; the VBUS pin is recessed in the receptacle.

## Layout guidance from datasheet

- §10.1: short, wide VIN1/VIN2/VOUT/GND traces; input and output caps close to the pins.

## Open questions

- None for block C. Whether `ST` goes to the RP2350 is block E's call (1 GPIO).
