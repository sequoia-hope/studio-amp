# Decisions

Every non-obvious decision, logged as it is made. Newest at the bottom.

| Date | Decision | Why | Alternatives considered |
|---|---|---|---|
| 2026-11-07 | Variant A = integrated PoE PD chip + isolated active-clamp forward + 48 V amp rail + GW1N-9 + all GaN | User's choice; the variant to focus on. ACF is the spec's preferred topology for ~70 W efficiency; 48 V gives ≈144 W peak BTL into 8 Ω, over the >100 W target | Flyback; 36/42 V rails; iCE40 HX8K; discrete PD (later variant) |
| 2026-11-07 | One board, full satellite spec (not core-only, not split) | User: "one board for now, studio monitor version, not sub" | Core-first subset; separate power and compute boards |
| 2026-11-07 | Headphone/line DAC = FPGA 1-bit stream, reclocked on a quiet rail, discrete filter | User chose; matches the discrete-first rule and the UcD-variant signal chain | I2S DAC chip; both as variants |
| 2026-11-07 | Open source, public repo sequoia-hope/studio-amp, MIT | User chose "public repo now" | Local only |
| 2026-11-07 | JLCPCB, 5 prototypes, 2-sided assembly, ≥4 layers, cost secondary | User chose | 1-sided cost-aware build |
| 2026-11-07 | Project converted in place to a Boardroom board repo (template, vendored skill, pcbview 26ba32b and ultraroute b38a039 pinned as in boardroom 66be834) | new-board.sh refuses a non-empty dir, and the folder already held the proj registration (serve.sh, launch.sh, git history); did the same steps by hand. launch.sh stays tracked | Make a fresh repo and copy the spec over |
| 2026-11-07 | Gate driver LMG1210RVRR (C2677136) instead of uP1966 | uP1966E has 0 stock on every LCSC listing; LMG1210 is an in-stock half-bridge GaN driver; user chose it | LMG1205 (BGA, 485 stock); sourcing uP1966 elsewhere |
| 2026-11-07 | Variant A audio targets relaxed for open-loop PWM + feedforward (R-51), with an optional post-filter sense path | Phase 0 review M3: studio-monitor THD/noise not reachable open-loop; user accepted | Closed-loop feedback in variant A |
| 2026-11-07 | Full performance specified at Class 6; Class 8 used as headroom; LEDs 5 W, firmware-limited per class | Phase 0 review B1/M6: budget didn't close; Type 4 PSEs are rare | Class 8 baseline with 10 W LEDs |
| 2026-11-07 | Display header: 8-pin (ST7735S 0.96 in 80×160 IPS TFT), not the spec's 7-pin OLED | User named the module; these carry a BLK backlight pin. All signal pins on FPGA I/O and GND/VCC on solder jumpers, so a module with a different pin order still works | 7-pin SSD1331/SSD1351 OLED header |
| 2026-11-07 | Architecture: RP2350B; FPGA bitstreams held in the RP2350 flash and loaded over SSPI; PHY RMII to the FPGA MAC; one digital isolator for PD status; silicon MOSFETs in the converter, GaN only in the audio stage | See design/architecture.md, 'Architecture decisions' | RP2350A; separate FPGA config flash; RMII to the RP2350 |
