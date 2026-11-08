# ESD and TVS parts used across block G (passive group)

Datasheets: datasheets/pesd5v0s1bl.pdf (Nexperia), datasheets/srv05-4.pdf (Semtech),
datasheets/usblc6-2sc6.pdf (ST), datasheets/mdd-smf5.0a.pdf (MDD). Read: characteristics,
application notes, layout.

| Part | Where | Key specs (datasheet) | Supplier line |
|---|---|---|---|
| PESD5V0S1BL,315 (DFN1006-2, bidirectional) | knob ×8, LED D/C ×2, SWD ×2, UART ×2 | VRWM 5 V; VBR 5.5–9.5 V; IRM ≤ 100 nA; Cd 35 typ / 45 pF max; VCL 14 V; IEC 61000-4-2 30 kV contact (abs), level 4; IPPM 12 A (8/20 µs) | `C84374 PESD5V0S1BL,315 (Nexperia, DFN1006-2): extended, JLC stock 76124, lifecycle normal, checked 2026-11-07` |
| SRV05-4.TCT (SOT-23-6, 4 lines + rail) | Qwiic SDA/SCL, display ×2, JTAG | VRWM 5 V; IR ≤ 5 µA; Cj 3 typ / 5 pF max; VC 12.5 V at 1 A, 17.5 V at 5 A; IEC ±8 kV contact / ±15 kV air; 12 A (8/20 µs) | `C13612 SRV05-4.TCT (SEMTECH, SOT-23-6L): extended, JLC stock 66821, lifecycle normal, checked 2026-11-07` |
| USBLC6-2SC6 (SOT-23-6) | USB D+/D− | see G-usb-c.md | `C7519 USBLC6-2SC6 (ST, SOT-23-6L): extended, JLC stock 25409, lifecycle normal, checked 2026-11-07` |
| SMF5.0A (SOD-123FL, unidirectional) | VUSB, +5V_LED | VRWM 5.0 V; VBR 6.4–7.0 V; IR ≤ 400 µA at VRWM; VC 9.2 V at 21.7 A; 200 W | `C193402 SMF5.0A (MDD(Microdiode Semiconductor), SOD-123FL): extended, JLC stock 472221, lifecycle normal, checked 2026-11-07` |

Multi-sourced: PESD5V0S1BL has BORN, TECH PUBLIC and UMW equivalents (C314269, C2912556, C2931142);
SRV05-4 has hongjiacheng, TECH PUBLIC and MSKSEMI (C7420376 preferred, C558418, C2836319);
USBLC6-2SC6 has UMW and TECH PUBLIC (C2687116, C2827654); SMF5.0A has several makers. All are
footprint-compatible per their listings. Read each maker's sheet before substituting.

## Selection rules applied

- Standoff ≥ the highest normal signal: all signals are 3.3 V or 5 V. 5 V VRWM parts. The +5V_LED
  rail uses **SMF6.0A** (VRWM 6.0 V, VBR 6.67–7.37 V, VC 10.3 V at 19.4 A; C123790, MDD, 83315 stock)
  after the review, so it sits below stand-off (IR ≤ 400 µA at VRWM, less at 5.12 V, not zero) (G-led-out.md).
- Capacitance against the signal: I2C (bus-capacitance-limited) and SPI to the display (≤ 15 MHz,
  many lines) get the 3 pF SRV05-4. Slow lines (knobs, encoders, UART, SWD, LED data with 47 Ω) get
  the 35 pF PESD5V0S1BL. USB gets the USBLC6 (3.5 pF max, HS-rated).
- Clamp vs downstream: every protected line passes a series resistor (33 Ω–1 kΩ) before an IC pin,
  except Qwiic B side (see G-qwiic.md, the TCA9617B's ±4 kV HBM) and the USB data lines (USB 2.0
  needs ≤ 27 Ω, block E's).
- SRV05-4 pin 5: tied to the line's own supply rail (Semtech "option 1"): +3V3 (display, JTAG) or
  QWIIC_3V3 (Qwiic). Its internal TVS then also clamps that rail.

## Layout (from the datasheets and domains/io-protection.md)

- At the connector pins, before any series R. Each GND pad gets its own via to the plane.
- USBLC6: ≤ a few mm of trace on I/O, VBUS and GND (its layout section's ≈ 6 nH per path adds
  L·di/dt to the clamp).
