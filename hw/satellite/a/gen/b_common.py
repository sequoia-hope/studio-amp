"""b_common.py -- shared helpers for block B's sheets (gen/iso_dcdc.py, gen/iso_aux.py).

B wraps hier.SubSheet with the b_parts catalogue (Value, Footprint, MPN, Manufacturer, LCSC on
every part) and a few field-placement modes; lm5019_buck() draws the LM5019 bias buck used twice
(VB_PRI on the primary, iso_dcdc; VSR on the secondary, iso_aux). Design: design/parts/B-bias.md.
"""
from __future__ import annotations

from b_parts import P, fields
from hier import S, Sym, new_uuid


class B:
    """Thin layer over hier.SubSheet: catalogue parts, rails and field placement."""

    def __init__(self, sch):
        self.s = sch

    def part(self, lib, ref, key, at, rot=0, mirror=None, extra=None, value=None, dnp=False,
             tf="r", **kw):
        """tf: where Reference/Value go. r = right (KiCad default here), l = left, v / vl =
        vertical text right / left of a vertical part (crowded rows), h = above and below a
        horizontal two-pin part, n = positions given in kw."""
        val, fp, *_ = P[key]
        x, y = at
        g = 2.54 if dnp else 0.0          # keep text clear of KiCad's DNP cross
        if tf == "l":
            kw.update(ref_at=(x - 2.54 - g, y - 1.27), value_at=(x - 2.54 - g, y + 1.27), justify="right")
        elif tf in ("v", "vl"):
            # vertical text beside a vertical part, centred a little high so it clears the
            # ground symbol's net name below the part
            rr = 0 if rot in (90, 270) else 90
            yc = y if rot in (90, 270) else y - 3.81
            xs_ = (x + 2.03 + g, x + 3.81 + g) if tf == "v" else (x - 3.81 - g, x - 2.03 - g)
            kw.update(ref_at=(xs_[0], yc), value_at=(xs_[1], yc), ref_rot=rr, justify="")
        elif tf == "h":
            kw.update(ref_at=(x, y - 2.54), value_at=(x, y + 2.54), justify="")
        elif tf == "ha":
            kw.update(ref_at=(x, y - 5.08), value_at=(x, y - 2.54), justify="")
        if dnp:
            val = val + " DNP"
        return self.s.symbol(lib, ref, value or val, at, rot=rot, mirror=mirror, footprint=fp,
                             fields=fields(key, extra), dnp=dnp, **kw)

    def R(self, ref, key, at, rot=0, **kw):
        if rot in (90, 270):
            kw.setdefault("tf", "h")
        return self.part("Device:R", ref, key, at, rot, **kw)

    def C(self, ref, key, at, rot=0, pol=False, **kw):
        if rot in (90, 270):
            kw.setdefault("tf", "h")
        return self.part("Device:C_Polarized" if pol else "Device:C", ref, key, at, rot, **kw)

    def gnd(self, at):
        return self.s.power("power:GND", at)

    def rtn(self, at):
        """Primary return: a GND-shaped symbol named VPRI_RTN, net name below it."""
        p = self.s.power("power:GND", at, value="VPRI_RTN")
        for prop in p.node:
            if isinstance(prop, list) and prop and str(prop[0]) == "property" and prop[1] == "Value":
                prop[3] = S("at", at[0], at[1] + 3.81, 0)
        return p

    def vcc(self, at, net):
        return self.s.power("power:VCC", at, value=net)

    def flag(self, at):
        return self.s.power("power:PWR_FLAG", at)

    def w(self, *pts):
        self.s.wire(*pts)

    def lab(self, name, at, rot=0):
        self.s.label(name, at, rot)

    def glab(self, name, at, rot, shape):
        self.s.label(name, at, rot, kind="global_label", shape=shape)

    def dashed(self, a, b, width=0.3):
        self.s.items.append(S("polyline", S("pts", S("xy", *a), S("xy", *b)),
                              S("stroke", S("width", width), S("type", Sym("dash"))), S("uuid", new_uuid())))


def lm5019_buck(b, dx, dy, refs, vals, vin, vout, ret, title, note):
    """LM5019 buck with Type III ripple injection, drawn with U at (68.58 + dx, 271.78 + dy).
    refs: U, L, RON, RFBT, RFBB, RUVT, RUVB, RR, CIN, CIN2, CVCC, CBST, COUT, CR, CAC.
    vals: b_parts keys for RON, RFBT, RUVT, RR, L. ret: b.gnd or b.rtn."""
    def p(x, y):
        return (round(x + dx, 2), round(y + dy, 2))
    R, C, w, vcc = b.R, b.C, b.w, b.vcc
    u = refs["U"]
    ub = b.part("Regulator_Switching:LM5017MR", u, "LM5019", p(68.58, 271.78), value="LM5019",
                tf="n", ref_at=p(60.96, 256.54), value_at=p(60.96, 259.08), justify="left")
    xr = 43.18
    vcc(p(xr, 251.46), vin)
    w(p(xr, 251.46), p(xr, 280.67))
    vinb = ub.pin("2")
    w(p(xr, 259.08), p(55.88, 259.08), (vinb[0] - 2.54, vinb[1]), vinb)
    r = R(refs["RON"], vals["RON"], p(50.8, 264.16), tf="vl")
    w(p(50.8, 259.08), r.pin("1"))
    w(r.pin("2"), (r.pin("2")[0], ub.pin("4")[1]), ub.pin("4"))
    c1 = C(refs["CIN"], "1u100", p(38.1, 266.7), extra={"Decouples": f"{u}.2"}, tf="v")
    c2 = C(refs["CIN2"], "100n100", p(27.94, 266.7), extra={"Decouples": f"{u}.2"}, tf="vl")
    w(p(xr, 261.62), p(38.1, 261.62), p(27.94, 261.62))
    w(p(38.1, 261.62), c1.pin("1"))
    w(p(27.94, 261.62), c2.pin("1"))
    w(c2.pin("2"), p(27.94, 273.05), p(38.1, 273.05), c1.pin("2"))
    ret(p(33.02, 273.05))
    ru1 = R(refs["RUVT"], vals["RUVT"], p(xr, 284.48), tf="l")
    ru2 = R(refs["RUVB"], "10k", p(xr, 299.72), tf="l")
    w(ru1.pin("2"), ru2.pin("1"))
    w(p(xr, 292.1), p(55.88, 292.1), (ub.pin("3")[0] - 2.54, ub.pin("3")[1]), ub.pin("3"))
    ret(ru2.pin("2"))
    w(ub.pin("1"), p(66.04, 287.02), p(68.58, 287.02), ub.pin("9"))
    ret(p(68.58, 287.02))
    bst, swp, fbp, vccp = ub.pin("7"), ub.pin("8"), ub.pin("5"), ub.pin("6")
    cb = C(refs["CBST"], "10n", p(83.82, 261.62), tf="vl")
    w(bst, (cb.pin("2")[0], bst[1]), cb.pin("2"))
    w(cb.pin("1"), p(83.82, 255.27), p(91.44, 255.27), (p(91.44, 0)[0], swp[1]))
    w(swp, (p(91.44, 0)[0], swp[1]))
    lb = b.part("Device:L", refs["L"], vals["L"], (p(97.79, 0)[0], swp[1]), rot=90, tf="n",
                ref_at=(p(97.79, 0)[0], swp[1] + 3.81), value_at=(p(97.79, 0)[0], swp[1] + 6.35), justify="")
    w(p(91.44, 269.24), lb.pin("1"))
    xo = p(114.3, 0)[0]
    w(lb.pin("2"), (xo, swp[1]))
    cv = C(refs["CVCC"], "1u", p(83.82, 284.48), extra={"Decouples": f"{u}.6"}, tf="v")
    w(vccp, (cv.pin("1")[0], vccp[1]), cv.pin("1"))
    ret(cv.pin("2"))
    rf1 = R(refs["RFBT"], vals["RFBT"], p(114.3, 279.4), tf="v")
    rf2 = R(refs["RFBB"], "10k", p(114.3, 294.64), tf="n", ref_at=p(116.33, 294.0), value_at=p(118.11, 294.0),
            ref_rot=90, justify="")
    w((xo, swp[1]), rf1.pin("1"))
    w(rf1.pin("2"), rf2.pin("1"))
    ret(rf2.pin("2"))
    w(p(114.3, 287.02), p(88.9, 287.02), (p(88.9, 0)[0], fbp[1]), fbp)
    co = C(refs["COUT"], "10u", p(121.92, 276.86), tf="v")
    w((xo, swp[1]), p(121.92, 269.24), co.pin("1"))
    ret(co.pin("2"))
    vcc(p(121.92, 264.16), vout)
    w(p(121.92, 264.16), p(121.92, 269.24))
    b.flag(p(127.0, 246.38))
    w(p(114.3, 246.38), p(127.0, 246.38))
    rr = R(refs["RR"], vals["RR"], p(99.06, 246.38), rot=90, tf="n", ref_at=p(99.06, 248.92),
           value_at=p(99.06, 251.46), justify="")
    cr = C(refs["CR"], "1n", p(109.22, 246.38), rot=90, tf="ha")
    w(p(91.44, 255.27), p(91.44, 246.38), rr.pin("1"))
    w(rr.pin("2"), cr.pin("1"))
    w(cr.pin("2"), p(114.3, 246.38), p(114.3, 269.24))
    ca = C(refs["CAC"], "100n", p(104.14, 260.35), tf="v")
    w(p(104.14, 246.38), ca.pin("1"))
    w(ca.pin("2"), p(104.14, 287.02))
    b.s.text(note, p(22.86, 312.42))
    b.s.box(p(20.32, 233.68), p(132.08, 327.66), title)
    return ub
