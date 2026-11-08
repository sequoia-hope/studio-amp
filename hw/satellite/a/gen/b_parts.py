"""b_parts.py -- block B parts catalogue for gen/iso_dcdc.py and gen/iso_aux.py.

Each entry: (value, footprint, MPN, manufacturer, LCSC). LCSC numbers were checked with
jlc_parts.py on 2026-11-08; the electrical choices come from design/parts/B-*.md.
"""

R0603 = "Resistor_SMD:R_0603_1608Metric"
R0805 = "Resistor_SMD:R_0805_2012Metric"
R2512 = "Resistor_SMD:R_2512_6332Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"
C1206 = "Capacitor_SMD:C_1206_3216Metric"
C1210 = "Capacitor_SMD:C_1210_3225Metric"
UR = "UNI-ROYAL"


def r8(val, code, lcsc):
    return (f"{val} 1% 0805", R0805, f"0805W8F{code}T5E", UR, lcsc)


def r(val, code, lcsc):
    return (f"{val} 1% 0603", R0603, f"0603WAF{code}T5E", UR, lcsc)


P = {
    # ---- resistors, 0603 1 % (UNI-ROYAL 0603WAF)
    "31k6": r("31.6k", "3162", "C25967"), "14k3": r("14.3k", "1432", "C22799"),
    "4k53": r("4.53k", "4531", "C25971"), "316k": r("316k", "3163", "C25814"),
    "1k": r("1k", "1001", "C21190"), "73k2": r("73.2k", "7322", "C14890"),
    "2k37": r("2.37k", "2371", "C25964"), "47k": r("47k", "4702", "C25819"),
    "470k": r("470k", "4703", "C23178"), "23k7": r("23.7k", "2372", "C22912"),
    "4k99": r("4.99k", "4991", "C23046"), "10k": r("10k", "1002", "C25804"),
    "100k": r("100k", "1003", "C25803"), "267k": r("267k", "2673", "C22963"),
    "107k": r("107k", "1073", "C14889"), "237k": r("237k", "2373", "C22914"),
    "200k": r("200k", "2003", "C25811"), "750": r("750", "7500", "C23241"),
    "2k": r("2k", "2001", "C22975"), "88k7": r("88.7k", "8872", "C23258"),
    "4k22": r("4.22k", "4221", "C23042"), "5k9": r("5.9k", "5901", "C23071"),
    "115k": r("115k", "1153", "C22783"), "499": r("499", "4990", "C23065"),
    "1M": r("1M", "1004", "C22935"), "866k": r("866k", "8663", "C23257"),
    "3k9": r("3.9k", "3901", "C23018"), "3k3": r("3.3k", "3301", "C22978"),
    "15k": r("15k", "1502", "C22809"), "280k": r("280k", "2803", "C22970"),
    "71k5": r("71.5k", "7152", "C23103"), "51k1": r("51.1k", "5112", "C23072"),
    "82k": r("82k", "8202", "C23254"), "100R": r("100", "1000", "C22775"),
    # 0805 (150 V working, 300 V overload) for resistors that see VPRI / VBUS or the N5 transient
    # (phase 2 review B-m1): 0603 is rated 75 V working
    "73k2_8": r8("73.2k", "7322", "C17814"), "47k_8": r8("47k", "4702", "C17713"),
    "470k_8": r8("470k", "4703", "C17709"), "100k_8": r8("100k", "1003", "C149504"),
    "267k_8": r8("267k", "2673", "C17585"), "237k_8": r8("237k", "2373", "C17568"),
    "280k_8": r8("280k", "2803", "C17597"), "51k1_8": r8("51.1k", "5112", "C17731"),
    "0R": ("0R 0603", R0603, "0603WAF0000T5E", UR, "C21189"),
    "2R2": ("2.2R 1% 0603", R0603, "RC0603FR-072R2L", "YAGEO", "C112307"),
    # precision 0.1 % thin film (CV divider, droop divider)
    "47k5_p": ("47.5k 0.1% 0805", R0805, "RT0805BRD0747K5L", "YAGEO", "C865514"),   # 44 mW: 0805 (B-feedback)
    "2k61_p": ("2.61k 0.1% 0603", R0603, "RT0603BRD072K61L", "YAGEO", "C861301"),
    "150k_p": ("150k 0.1% 0805", R0805, "RT0805BRD07150KL", "YAGEO", "C136927"),
    "10k_p": ("10.0k 0.1% 0603", R0603, "RT0603BRD0710KL", "YAGEO", "C95204"),
    # power resistors
    "Rcs": ("68m 1% 2512 2W", R2512, "RLP25FEER068", "TA-I Tech", "C2683389"),
    "Rsh": ("30m 1% 2512 2W", R2512, "LR122WF300MT4E", "UNI-ROYAL", "C2941066"),
    "Rsnub": ("47R 5% 2512 1W", R2512, "25121WJ0470T4E", "UNI-ROYAL", "C15261"),
    # ---- capacitors
    "220n": ("220n 25V X7R 0603", C0603, "CL10B224KA8NNNC", "Samsung", "C21120"),
    "1u": ("1u 25V X7R 0603", C0603, "CL10B105KA8NNNC", "Samsung", "C29936"),
    "10u": ("10u 25V X7R 1206", C1206, "CL31B106KAHNNNE", "Samsung", "C14860"),
    "82p": ("82p 50V C0G 0603", C0603, "0603CG820J500NT", "FH", "C1683"),
    "6n8": ("6.8n 50V X7R 0603", C0603, "0603B682K500NT", "FH", "C1631"),
    "47n": ("47n 50V X7R 0603", C0603, "CL10B473KB8NNNC", "Samsung", "C1622"),
    "100n": ("100n 50V X7R 0603", C0603, "CL10B104KB8NNNC", "Samsung", "C1591"),
    "100n100": ("100n 100V X7R 0603", C0603, "CL10B104KC8NNNC", "Samsung", "C15725"),
    "1n": ("1n 50V C0G 0603", C0603, "CL10C102JB8NNNC", "Samsung", "C163508"),
    "10n": ("10n 50V X7R 0603", C0603, "CL10B103KB8NNNC", "Samsung", "C1589"),
    "1u100": ("1u 100V X7R 0805", C0805, "HMK212BC7105KGHTE", "Taiyo Yuden", "C385977"),
    "470n": ("470n 16V X7R 0603", C0603, "CL10B474KO8NNNC", "Samsung", "C105526"),
    "4n7": ("4.7n 50V X7R 0603", C0603, "CL10B472KB8NNNC", "Samsung", "C1621"),
    "33p": ("33p 50V C0G 0603", C0603, "CL10C330JB8NNNC", "Samsung", "C1663"),
    "470p": ("470p 50V C0G 0603", C0603, "CL10C471JB8NNNC", "Samsung", "C27694"),
    "33n": ("33n 50V X7R 0603", C0603, "CL10B333KB8NNNC", "Samsung", "C21117"),
    "4u7_100": ("4.7u 100V X7S 1210", C1210, "GCM32DC72A475KE02L", "Murata", "C913445"),
    "100n250": ("100n 250V X7R 1206", C1206, "GRM31CR72E104KW03L", "Murata", "C97956"),
    "10n250": ("10n 250V X7R 1206", C1206, "1206B103K251NT", "FH", "C913956"),
    "22p250": ("22p 250V C0G 0805", C0805, "CC0805JRNPOYBN220", "YAGEO", "C90626"),
    "Ycap": ("2.2n Y2/X1 250VAC 2220", "Capacitor_SMD:C_2220_5750Metric", "GA355QR7GF222KW01L", "Murata", "C91600"),
    "47u100": ("47u 100V 105C", "Capacitor_SMD:CP_Elec_10x10.5", "RVT2A470M1010", "Honor Elec", "C87862"),
    "bulk": ("1000u 63V KZN 105C", "Capacitor_THT:CP_Radial_D16.0mm_P7.50mm", "EKZN630ELL102ML25S", "Nippon Chemi-Con", "C337254"),
    # ---- semiconductors
    "UCC2897A": ("UCC2897APWR", "Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm", "UCC2897APWR", "Texas Instruments", "C54444"),
    "LM5019": ("LM5019", "Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.95x4.9mm_Mask2.71x3.4mm", "LM5019MRX/NOPB", "Texas Instruments", "C471034"),
    "FDMS86200": ("FDMS86200 150V", "Package_SON:Infineon_PG-TDSON-8_6.15x5.15mm", "FDMS86200", "onsemi", "C128799"),
    "IRFR6215": ("IRFR6215 -150V", "Package_TO_SOT_SMD:TO-252-2", "IRFR6215TRLPBF", "Infineon", "C537989"),
    "BSC500": ("BSC500N20NS3 200V", "Package_SON:Infineon_PG-TDSON-8_6.15x5.15mm", "BSC500N20NS3GATMA1", "Infineon", "C5381902"),
    "NCP4306": ("NCP4306DADZZDA", "Package_TO_SOT_SMD:SOT-23-6", "NCP4306DADZZDASNT1G", "onsemi", "C504885"),
    "INA281A4": ("INA281A4", "Package_TO_SOT_SMD:SOT-23-5", "INA281A4IDBVR", "Texas Instruments", "C2864421"),
    "TL431B": ("TL431B", "Package_TO_SOT_SMD:SOT-23", "TL431BIDBZR", "Texas Instruments", "C41283"),
    "LTV217": ("LTV-217-B", "Package_SO:SOP-4_4.4x2.6mm_P1.27mm", "LTV-217-B-G", "Lite-On", "C115450"),
    "AO3400A": ("AO3400A", "Package_TO_SOT_SMD:SOT-23", "AO3400A", "AOS", "C20917"),
    "2N7002": ("2N7002", "Package_TO_SOT_SMD:SOT-23", "2N7002", "JSCJ", "C8545"),
    "BAS316": ("BAS316", "Diode_SMD:D_SOD-323", "BAS316,115", "Nexperia", "C109218"),
    "BAV21W": ("BAV21W 250V", "Diode_SMD:D_SOD-123", "BAV21W", "MDD", "C113947"),
    "US1G": ("US1G 400V", "Diode_SMD:D_SMA", "US1G", "Jingdao", "C383015"),
    "SMBJ130A": ("SMBJ130A", "Diode_SMD:D_SMB", "SMBJ130A-E3/52", "Vishay", "C553984"),
    "SMCJ51A": ("SMCJ51A", "Diode_SMD:D_SMC", "SMCJ51A", "MDD", "C408371"),
    # ---- magnetics
    "T1": ("750343576 (1:2)", "studio_B:Wurth_750343576_ER19", "750343576", "Würth Elektronik", "HAND"),
    "Lout": ("68u CDRH127/LDNP", "studio_B:L_Sumida_CDRH127", "CDRH127/LDNP-680MC", "Sumida", "C2452974"),
    "L330": ("330u 0.34A", "studio_B:L_SXN_SM5845", "SM5845-331MT", "SXN", "C10124"),
    "L220": ("220u 0.36A", "studio_B:L_SXN_SM5845", "SM5845-221MT", "SXN", "C10123"),
    # ---- iso_aux logic
    "HT7550": ("HT7550-1 5V", "Package_TO_SOT_SMD:SOT-89-3", "HT7550-1", "Holtek", "C16106"),
    "LVC1GU04": ("74LVC1GU04", "Package_TO_SOT_SMD:SOT-23-5", "SN74LVC1GU04DBVR", "Texas Instruments", "C81934"),
    "HC4017": ("74HC4017", "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm", "74HC4017D,653", "Nexperia", "C148206"),
    "LVC1G123": ("74LVC1G123", "Package_SO:SSOP-8_2.95x2.8mm_P0.65mm", "SN74LVC1G123DCTR", "Texas Instruments", "C123302"),
    "LVC1G08": ("74LVC1G08", "Package_TO_SOT_SMD:SOT-23-5", "SN74LVC1G08DBVR", "Texas Instruments", "C7666"),
    "LVC2G08": ("74LVC2G08", "Package_SO:TSSOP-8_3x3mm_P0.65mm", "74LVC2G08DP,125", "Nexperia", "C406037"),
    "LM393": ("LM393", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", "LM393DR2G", "onsemi", "C7955"),
    "XTAL": ("7.3728MHz 20pF", "Crystal:Crystal_SMD_HC49-SD", "SXMH7.3728F2020F30", "SCTF", "C2901749"),
}


def fields(key: str, extra: dict | None = None) -> dict:
    _, _, mpn, mfr, lcsc = P[key]
    f = {"MPN": mpn, "Manufacturer": mfr, "LCSC": lcsc}
    if lcsc == "HAND":
        f["Supplier"] = "Würth direct / Digi-Key / Mouser (hand-soldered)"
    if extra:
        f.update(extra)
    return f
