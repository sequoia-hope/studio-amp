# D/C (×4 each) — LMG1210 bootstrap: BAT46WJ Schottky + 470 nF bootstrap capacitor (IGC033S10S1, 448 kHz)

> **UPDATE 2026-11-08 — GaN back to IGB070S10S1 (user), fsw 576 kHz. This block supersedes the IGC033 figures below where they differ; part values are unchanged and remain valid for the IGC033 fallback.**
> - Q per cycle = 0.5 + QgH **7.9 nC** + IHB 0.85 mA × 1.60 µs (1.36) + 0.08 = **9.8 nC**. C_BST 470 nF (≈ 375 nF effective) → droop 26 mV. VDD ≥ 5 × 375 nF ✓ (unchanged parts).
> - Refresh at the 8–92 % clamp, 576 kHz: LO ≥ 0.08/576 kHz − 26 ns = **113 ns** → 9.8 nC/113 ns = **0.087 A** → BAT46WJ VF (log-interpolated between 50 and 250 mA) ≈ 0.52 V typ / 0.60 V max; RSW 0.035 V → equilibrium HB−HS ≥ 4.75 − 0.60 − 0.035 − 0.026 = **4.09 V** worst case (≥ 3.80 V ROC ✓, ≥ 0.44 V above UVLO max); typical 4.42 V.
> - **VBST maximum (Eq. 3):** VDD 5.25 − VF 0.10 (at equilibrium current → 0) + 16 A × 10.5 mΩ (IGB070 Rds at 100 °C) = **5.32 V**. At the 13 A legitimate peak: 5.29 V; at VDD 5.0 V typ: 5.04–5.07 V. That is above the LMG1210 HB−HS ROC max 5.25 V by up to 0.07 V, 0.18 V below the LMG1210 abs max 5.5 V and the IGB070 recommended VGS max 5.5 V. Condition (second-pass review n-1): it needs a **long LO (low HS duty, so the recharge current and VF fall to ≈ 0.1 V) and ≥ 14 A flowing out of the switch node through the LS in reverse at the same moment**, i.e. reactive or fault current against the drive direction, not the normal high-duty peak; plus VDD at its +5 % limit. **Accepted and flagged** for the reviewer. A higher-low-current-VF diode would cost refresh margin, which is the binding side (above).

> **fsw update (block E review, ECP5 −7I grid now 1.695 ns, PLL ×12): baseline fsw = 576 kHz (12 × 48 kHz, 1024 steps); 768 kHz option; 448/512/672 kHz only with E's ×14 bring-up option.** At 576 kHz: Q = 0.5 + 14 + 0.85 mA × 1.60 µs (1.36) + 0.08 = **15.9 nC**; LO ≥ 0.08/576 kHz − 26 ns = **113 ns** → 0.141 A → BAT46WJ VF ≈ 0.57 typ / 0.68 V max, RSW drop 0.06 V → equilibrium HB−HS ≥ 4.75 − 0.68 − 0.06 − 0.042 = **3.97 V** worst case (≥ 3.80 V ROC ✓, ≥ 0.32 V above UVLO max). Typical 5.0 − 0.57 − 0.06 = 4.37 V. Accepted; if the bench shows less, widen the clamp to 9–91 % (LO ≥ 130 ns).

Revision note: rewritten after the phase 1 review (M1, m7, n4): GaN IGC033S10S1, duty clamp 8–92 %, HS gate pull-down 100 kΩ, diode VF taken at the real recharge current.

## D_BST — Nexperia BAT46WJ (100 V Schottky)
Datasheet: datasheets/bat46wj.pdf. Read: all.
Supplier: `C114696 BAT46WJ,115 (Nexperia, SOD-323F): extended, JLC stock 57004, lifecycle normal, checked 2026-11-07`. Footprint SOD-323F (flat leads).
| Parameter | Rating | Our worst case | OK |
|---|---|---|---|
| VR | 100 V | switch node 48 V; TVS clamp 82.4 V + ring ≤ 21 V → ≈ 103 V for ns (same event the GaN rides on its 120 V pulsed rating, D-gan-fet.md m3) | ✓ normal; transient as for the GaN |
| IF | 250 mA | recharge pulse ≈ 0.11 A for ≤ 153 ns per period (below); average 16.4 nC × 448 kHz = 7.3 mA | ✓ |
| IFSM | 2.5 A (< 10 ms) | start-up through the internal 1 kΩ | ✓ |
| VF (datasheet points) | 175 mV typ at 0.1 mA; 315/350 at 10 mA; 415/475 at 50 mA; 710/850 at 250 mA | interpolated log-linear at 0.11 A: **≈ 0.54 V typ, 0.64 V max** | used below |
| Cd | 39 pF max at 0 V | switching loss ½·C·V²·f ≈ 5 mW | ✓ |

## C_BST — Samsung CL10B474KA8NNNC (470 nF, 25 V, X7R, 0603)
Datasheet: datasheets/cl10b224ka8.pdf (Samsung CL series MLCC general spec, covers CL10B474KA8NNNC). Supplier: `C1623 CL10B474KA8NNNC (Samsung Electro-Mechanics, 0603): basic, JLC stock 1527065, lifecycle normal, checked 2026-11-07`.
Voltage 25 V ≥ 4.8× the 5.24 V max across it ✓. Effective at 5 V DC bias (20 % of rating, X7R 0603) taken as ≈ 80 % → **375 nF**.

## Calculations
### Charge per cycle (LMG1210 Eq. 7)
0.5 nC (HS dynamic) + Qrr 0 (Schottky) + QgH **14 nC** (IGC033 Qg max) + IHB 0.85 mA × ton,max 2.05 µs (= 0.92/448 kHz) = 1.74 nC + HS gate pull-down **100 kΩ** at 5 V (0.05 mA × 2.05 µs) = 0.10 nC → **Q = 16.3 nC per cycle** (16.4 used).
CBST,min (ΔV 0.1 V) = 164 nF → 470 nF (375 nF effective) → per-cycle droop **44 mV**.
VDD cap ≥ 5 × 375 nF = 1.9 µF effective → 2 × 2.2 µF X5R 0603 + 100 nF ≈ 2.9 µF (D-driver-passives.md) ✓.

### Refresh at maximum duty (review M1)
The bootstrap switch conducts only while LO is on, and LO = PWM low time − td (§7.3.3).
- Duty clamp 8–92 % (D-lmg1210.md): PWM low ≥ 179 ns → **LO ≥ 153 ns** at td max 26 ns.
- Average recharge current needed at sustained maximum duty: 16.4 nC/153 ns = **0.107 A**.
- At that current: BAT46WJ VF ≈ 0.54 V typ / 0.64 V max; bootstrap switch RSW 0.4 Ω (p.5, typ) × 0.107 A = 0.04 V.
- **Equilibrium HB−HS at sustained max duty = VDD − VF − RSW·I:** 5.0 − 0.54 − 0.04 = **4.42 V typ**; worst (VDD 4.75 V, VF max): 4.75 − 0.64 − 0.04 = **4.07 V**; minus the 44 mV within-cycle droop → **≥ 4.03 V**.
- Limits: LMG1210 ROC VHB−VHS ≥ 3.80 V ✓ (0.23 V margin); HS UVLO falling 3.30–3.65 V ✓ (≥ 0.38 V margin). IGC033 at VGS 4.0 V: Diagram 10 shows Rds(on) still near its plateau at 25 °C (≈ +10 %, hot ≈ +20 %) — accepted at the signal peaks only.
- With the old 3 % clamp: LO 47 ns, 0.35 A, VF ≈ 0.85–0.95 V → HB−HS ≈ 3.6–4.0 V (review M1). That is why the clamp was widened.
- Duty sits near the clamp for ≈ 9 % of a full-scale low-frequency cycle; equilibrium is reached in about ten periods, so the figure above is the design case, not a corner.

### VBST maximum (LMG1210 Eq. 3; review m7)
VBST = VDD − VF + IL·Rds(on) (IL > 0, LS in reverse conduction while LO is on). At equilibrium the recharge current falls towards zero, so VF → ≈ 0.10–0.17 V (175 mV typ at 0.1 mA): VBST,max = 5.25 − 0.10 + 16 A × 5.4 mΩ (IGC033 Rds at 100 °C) = **5.24 V**. Margin: 0.01 V to the LMG1210 ROC max (5.25 V), 0.26 V to the LMG1210 abs max and to the IGC033 recommended VGS max (both 5.5 V). Accepted: the ROC limit is touched only at VDD at its +5 % limit with 16 A of reverse current.

### Other charge paths (review n4)
The LMG1210's 1 kΩ across the bootstrap switch (§7.3.1) also conducts during the dead times, when VHS ≈ −VSD ≈ −3 V: ≈ 3 mA × 2 × 15 ns ≈ 0.1 nC per cycle. That is the only overcharge path, and it is negligible against the 44 mV droop per cycle.

## Bring-up
Scope HB−HS at 20 Hz full scale into 4 Ω (clamp duty), at VDRV 6.65 V; expect ≥ 4.0 V.

## Fine print
TI: for LS on-times < 20 ns use a synchronous GaN bootstrap (§8.2.2.2); ours is ≥ 153 ns. D_BST and C_BST as close to the pins as possible (§10.1).

## Open questions
None.
