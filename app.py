import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

# ============================================================
# MEDLAB AI DIAGNOSTICS HUB
# Professional CBC Clinical Decision Support — MVP
# ============================================================

st.set_page_config(
    page_title="MedLab AI Diagnostics",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# STYLE
# ============================================================

st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 25px;
        border-radius: 18px;
        border: 1px solid #30363d;
        background: linear-gradient(135deg, #161b22, #10151c);
        margin-bottom: 25px;
    }

    .hero-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .hero-subtitle {
        font-size: 18px;
        color: #9da7b3;
    }

    .metric-card {
        padding: 18px;
        border-radius: 15px;
        border: 1px solid #30363d;
        background: #161b22;
        text-align: center;
    }

    .metric-title {
        color: #9da7b3;
        font-size: 14px;
    }

    .metric-value {
        font-size: 28px;
        font-weight: 700;
    }

    .normal-box {
        padding: 18px;
        border-radius: 14px;
        background: #123524;
        border: 1px solid #238636;
        margin: 10px 0;
    }

    .warning-box {
        padding: 18px;
        border-radius: 14px;
        background: #3b2e0b;
        border: 1px solid #d29922;
        margin: 10px 0;
    }

    .danger-box {
        padding: 18px;
        border-radius: 14px;
        background: #3b1616;
        border: 1px solid #f85149;
        margin: 10px 0;
    }

    .info-box {
        padding: 18px;
        border-radius: 14px;
        background: #13263d;
        border: 1px solid #388bfd;
        margin: 10px 0;
    }

    .section-title {
        font-size: 27px;
        font-weight: 750;
        margin-top: 30px;
        margin-bottom: 15px;
    }

    .small-note {
        color: #8b949e;
        font-size: 13px;
    }

    div[data-testid="stMetric"] {
        background: #161b22;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 14px;
    }

    .footer {
        text-align: center;
        color: #6e7681;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #30363d;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="hero">
    <div class="hero-title">🧪 MedLab AI Diagnostics Hub</div>
    <div class="hero-subtitle">
        Professional CBC Clinical Decision Support System
    </div>
</div>
""", unsafe_allow_html=True)

st.warning(
    "⚠️ Ushbu tizim klinik qarorni qo‘llab-quvvatlovchi prototipdir. "
    "Natijalar laboratoriyaning o‘z reference intervalari, anamnez va klinik "
    "ko‘rik bilan birgalikda shifokor tomonidan baholanishi kerak. "
    "Bu dastur yakuniy tashxis yoki davolash o‘rnini bosmaydi."
)


# ============================================================
# SIDEBAR — PATIENT INFORMATION
# ============================================================

with st.sidebar:

    st.header("👤 Bemor ma’lumotlari")

    patient_name = st.text_input(
        "Bemor F.I.Sh.",
        placeholder="Ism Familiya"
    )

    patient_age = st.number_input(
        "Yosh",
        min_value=0,
        max_value=120,
        value=30,
        step=1
    )

    patient_sex = st.selectbox(
        "Jins",
        ["Erkak", "Ayol"]
    )

    complaints = st.text_area(
        "Shikoyatlar / klinik ma’lumot",
        placeholder="Masalan: holsizlik, isitma, yo‘tal, bosh aylanishi..."
    )

    diagnosis_context = st.text_area(
        "Qo‘shimcha klinik ma’lumot",
        placeholder="Anamnez, dori vositalari, surunkali kasalliklar..."
    )

    st.divider()

    st.caption(
        "Reference intervalar ushbu MVP uchun namunaviydir. "
        "Amaliyotda laboratoriyaning tasdiqlangan reference intervalari ishlatilishi kerak."
    )


# ============================================================
# CBC INPUTS
# ============================================================

st.markdown(
    '<div class="section-title">🩸 CBC natijalarini kiriting</div>',
    unsafe_allow_html=True
)

st.info(
    "💡 Natijalarni laboratoriya blankasidagi birliklarda kiriting. "
    "Flaglar namunaviy reference intervalarga asoslanadi."
)


# ------------------------------------------------------------
# REFERENCE INTERVAL FUNCTION
# ------------------------------------------------------------

def reference_ranges(age, sex):

    # Pediatric ranges are intentionally broad prototype ranges.
    # Real implementation should use validated age/sex/lab-specific ranges.

    if age < 1:
        return {
            "Hb": (10.0, 18.0),
            "RBC": (3.0, 5.5),
            "WBC": (5.0, 17.0),
            "PLT": (150, 450),
            "Neut": (20, 60),
            "Lymph": (30, 70),
            "MCV": (70, 110)
        }

    if age < 6:
        return {
            "Hb": (11.0, 14.5),
            "RBC": (3.8, 5.3),
            "WBC": (5.0, 15.0),
            "PLT": (150, 450),
            "Neut": (30, 60),
            "Lymph": (30, 60),
            "MCV": (70, 86)
        }

    if age < 12:
        return {
            "Hb": (11.5, 15.5),
            "RBC": (4.0, 5.2),
            "WBC": (4.5, 13.5),
            "PLT": (150, 450),
            "Neut": (35, 65),
            "Lymph": (25, 55),
            "MCV": (75, 95)
        }

    if age < 18:
        return {
            "Hb": (12.0, 16.0),
            "RBC": (4.0, 5.5),
            "WBC": (4.0, 11.0),
            "PLT": (150, 450),
            "Neut": (40, 70),
            "Lymph": (20, 50),
            "MCV": (78, 100)
        }

    if sex == "Erkak":
        return {
            "Hb": (13.5, 17.5),
            "RBC": (4.5, 5.9),
            "WBC": (4.0, 10.0),
            "PLT": (150, 400),
            "Neut": (40, 75),
            "Lymph": (20, 45),
            "MCV": (80, 100)
        }

    return {
        "Hb": (12.0, 15.5),
        "RBC": (4.0, 5.2),
        "WBC": (4.0, 10.0),
        "PLT": (150, 400),
        "Neut": (40, 75),
        "Lymph": (20, 45),
        "MCV": (80, 100)
    }


ranges = reference_ranges(patient_age, patient_sex)


# ============================================================
# INPUT SECTIONS
# ============================================================

st.subheader("🔴 Eritrotsit qatori")

c1, c2, c3 = st.columns(3)

with c1:
    hb = st.number_input(
        "Gemoglobin (g/dL)",
        min_value=0.0,
        max_value=30.0,
        value=13.0,
        step=0.1
    )

with c2:
    rbc = st.number_input(
        "RBC (×10¹²/L)",
        min_value=0.0,
        max_value=15.0,
        value=4.5,
        step=0.1
    )

with c3:
    hct = st.number_input(
        "Gematokrit (%)",
        min_value=0.0,
        max_value=80.0,
        value=42.0,
        step=0.1
    )


c4, c5, c6 = st.columns(3)

with c4:
    mcv = st.number_input(
        "MCV (fL)",
        min_value=0.0,
        max_value=150.0,
        value=90.0,
        step=0.1
    )

with c5:
    mch = st.number_input(
        "MCH (pg)",
        min_value=0.0,
        max_value=60.0,
        value=29.0,
        step=0.1
    )

with c6:
    mchc = st.number_input(
        "MCHC (g/dL)",
        min_value=0.0,
        max_value=50.0,
        value=33.0,
        step=0.1
    )


st.subheader("⚪ Leykotsit qatori")

c1, c2, c3 = st.columns(3)

with c1:
    wbc = st.number_input(
        "WBC (×10⁹/L)",
        min_value=0.0,
        max_value=100.0,
        value=7.0,
        step=0.1
    )

with c2:
    neut = st.number_input(
        "Neutrofil (%)",
        min_value=0.0,
        max_value=100.0,
        value=55.0,
        step=0.1
    )

with c3:
    lymph = st.number_input(
        "Limfotsit (%)",
        min_value=0.0,
        max_value=100.0,
        value=35.0,
        step=0.1
    )


c4, c5, c6 = st.columns(3)

with c4:
    mono = st.number_input(
        "Monotsit (%)",
        min_value=0.0,
        max_value=100.0,
        value=7.0,
        step=0.1
    )

with c5:
    eos = st.number_input(
        "Eozinofil (%)",
        min_value=0.0,
        max_value=100.0,
        value=2.0,
        step=0.1
    )

with c6:
    baso = st.number_input(
        "Bazofil (%)",
        min_value=0.0,
        max_value=100.0,
        value=1.0,
        step=0.1
    )


st.subheader("🟣 Trombotsit qatori")

c1, c2, c3 = st.columns(3)

with c1:
    plt = st.number_input(
        "Trombotsit (×10⁹/L)",
        min_value=0.0,
        max_value=1500.0,
        value=250.0,
        step=1.0
    )

with c2:
    mpv = st.number_input(
        "MPV (fL)",
        min_value=0.0,
        max_value=30.0,
        value=9.5,
        step=0.1
    )

with c3:
    rdw = st.number_input(
        "RDW-CV (%)",
        min_value=0.0,
        max_value=50.0,
        value=13.0,
        step=0.1
    )


# ============================================================
# ANALYSIS FUNCTIONS
# ============================================================

def flag(value, low, high):

    if value < low:
        return "LOW"

    if value > high:
        return "HIGH"

    return "NORMAL"


def flag_emoji(status):

    if status == "LOW":
        return "🔴"

    if status == "HIGH":
        return "🟠"

    return "🟢"


def severity_score(statuses):

    score = 0

    for status in statuses:

        if status == "LOW":
            score += 1

        elif status == "HIGH":
            score += 1

    return score


def analyze_cbc():

    results = []

    tests = [
        ("Gemoglobin", hb, ranges["Hb"], "g/dL"),
        ("RBC", rbc, ranges["RBC"], "×10¹²/L"),
        ("WBC", wbc, ranges["WBC"], "×10⁹/L"),
        ("Trombotsit", plt, ranges["PLT"], "×10⁹/L"),
        ("Neutrofil", neut, ranges["Neut"], "%"),
        ("Limfotsit", lymph, ranges["Lymph"], "%"),
        ("MCV", mcv, ranges["MCV"], "fL"),
    ]

    for name, value, interval, unit in tests:

        low, high = interval
        status = flag(value, low, high)

        results.append({
            "Ko‘rsatkich": name,
            "Natija": value,
            "Birlik": unit,
            "Pastki chegara": low,
            "Yuqori chegara": high,
            "Holat": status
        })

    return pd.DataFrame(results)


# ============================================================
# CALCULATED PARAMETERS
# ============================================================

anc = wbc * neut / 100
alc = wbc * lymph / 100

n_l_ratio = neut / lymph if lymph > 0 else 0

# approximate Mentzer index
mentzer = mcv / rbc if rbc > 0 else 0


# ============================================================
# ANALYZE BUTTON
# ============================================================

st.divider()

analyze = st.button(
    "🔬 CBC NI AI YORDAMIDA TAHLIL QILISH",
    type="primary",
    use_container_width=True
)


if analyze:

    df = analyze_cbc()

    statuses = df["Holat"].tolist()

    abnormal_count = sum(
        1 for x in statuses if x != "NORMAL"
    )

    # ========================================================
    # DASHBOARD
    # ========================================================

    st.markdown(
        '<div class="section-title">📊 Tahlil natijalari</div>',
        unsafe_allow_html=True
    )

    d1, d2, d3, d4 = st.columns(4)

    with d1:
        st.metric(
            "Abnormal ko‘rsatkichlar",
            abnormal_count
        )

    with d2:
        st.metric(
            "WBC",
            f"{wbc:.1f}"
        )

    with d3:
        st.metric(
            "Gemoglobin",
            f"{hb:.1f}"
        )

    with d4:
        st.metric(
            "Trombotsit",
            f"{plt:.0f}"
        )


    # ========================================================
    # TABLE
    # ========================================================

    st.markdown(
        '<div class="section-title">🧪 CBC panel</div>',
        unsafe_allow_html=True
    )

    display_df = df.copy()

    display_df["Flag"] = display_df["Holat"].apply(flag_emoji)

    display_df = display_df[
        [
            "Flag",
            "Ko‘rsatkich",
            "Natija",
            "Birlik",
            "Pastki chegara",
            "Yuqori chegara"
        ]
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # CALCULATED PARAMETERS
    # ========================================================

    st.markdown(
        '<div class="section-title">🧮 Hisoblangan ko‘rsatkichlar</div>',
        unsafe_allow_html=True
    )

    a1, a2, a3, a4 = st.columns(4)

    with a1:
        st.metric(
            "ANC",
            f"{anc:.2f} ×10⁹/L"
        )

    with a2:
        st.metric(
            "ALC",
            f"{alc:.2f} ×10⁹/L"
        )

    with a3:
        st.metric(
            "Neutrofil/Limfotsit",
            f"{n_l_ratio:.2f}"
        )

    with a4:
        st.metric(
            "Mentzer index",
            f"{mentzer:.1f}"
        )


    # ========================================================
    # CLINICAL PATTERN ENGINE
    # ========================================================

    st.markdown(
        '<div class="section-title">🧠 Klinik pattern tahlili</div>',
        unsafe_allow_html=True
    )

    findings = []
    recommendations = []


    # --------------------------------------------------------
    # ANEMIA
    # --------------------------------------------------------

    if hb < ranges["Hb"][0]:

        if mcv < 80:

            findings.append(
                "Gemoglobin pasaygan va MCV past: mikrotsitar anemiya patterni."
            )

            recommendations.append(
                "Ferritin, serum iron, transferrin saturation va retikulotsitlarni klinik holatga qarab ko‘rib chiqish."
            )

            if mentzer >= 13:
                recommendations.append(
                    "Mentzer indeksi ≥13 bo‘lishi temir tanqisligi foydasiga yo‘nalish berishi mumkin; yakuniy xulosa uchun qo‘shimcha tekshiruv zarur."
                )

            else:
                recommendations.append(
                    "Mentzer indeksi past bo‘lsa, talassemiya tashuvchiligi kabi differensial sabablarni ham ko‘rib chiqish mumkin."
                )

        elif mcv > 100:

            findings.append(
                "Gemoglobin pasaygan va MCV yuqori: makrotsitar anemiya patterni."
            )

            recommendations.append(
                "Vitamin B12, folat, jigar ko‘rsatkichlari, TSH va retikulotsitlarni klinik vaziyatga qarab baholash."
            )

        else:

            findings.append(
                "Gemoglobin pasaygan: normotsitar anemiya patterni."
            )

            recommendations.append(
                "Qon yo‘qotish, surunkali yallig‘lanish, buyrak faoliyati va retikulotsitlarni klinik kontekstda baholash."
            )


    # --------------------------------------------------------
    # LEUKOCYTOSIS
    # --------------------------------------------------------

    if wbc > ranges["WBC"][1]:

        findings.append(
            "Leykotsitoz aniqlangan."
        )

        if neut > ranges["Neut"][1]:

            findings.append(
                "Neutrofil ustunligi mavjud."
            )

            recommendations.append(
                "Infeksiya, yallig‘lanish, stress reaksiyasi va dori ta’sirini klinik belgilar bilan birga baholash."
            )


    # --------------------------------------------------------
    # LEUKOPENIA
    # --------------------------------------------------------

    if wbc < ranges["WBC"][0]:

        findings.append(
            "Leykopeniya aniqlangan."
        )

        if anc < 1.5:

            findings.append(
                f"ANC taxminan {anc:.2f} ×10⁹/L — neutropeniya ehtimolini ko‘rsatadi."
            )

            recommendations.append(
                "ANC qiymatini qayta tekshirish va klinik holatga qarab sabablarni baholash."
            )


    # --------------------------------------------------------
    # LYMPHOCYTOSIS
    # --------------------------------------------------------

    if lymph > ranges["Lymph"][1]:

        findings.append(
            "Limfotsitlar nisbiy ko‘paygan."
        )

        recommendations.append(
            "Virusli infeksiya va boshqa sabablarni klinik holat bilan birga baholash."
        )


    # --------------------------------------------------------
    # THROMBOCYTOPENIA
    # --------------------------------------------------------

    if plt < ranges["PLT"][0]:

        findings.append(
            "Trombotsitopeniya aniqlangan."
        )

        recommendations.append(
            "Periferik qon surtmasi, takroriy CBC va dori/infeksiya bilan bog‘liq sabablarni klinik vaziyatga qarab baholash."
        )

        if plt < 50:

            findings.append(
                "Trombotsitlar sezilarli darajada past."
            )

            recommendations.append(
                "Qon ketish belgilari mavjud bo‘lsa shoshilinch klinik baholash zarur."
            )


    # --------------------------------------------------------
    # THROMBOCYTOSIS
    # --------------------------------------------------------

    if plt > ranges["PLT"][1]:

        findings.append(
            "Trombotsitoz aniqlangan."
        )

        recommendations.append(
            "Reaktiv trombotsitoz sabablari, jumladan infeksiya, yallig‘lanish va temir tanqisligini klinik kontekstda baholash."
        )


    # --------------------------------------------------------
    # EOSINOPHILIA
    # --------------------------------------------------------

    if eos >= 6:

        findings.append(
            "Eozinofillar ko‘paygan."
        )

        recommendations.append(
            "Allergik kasalliklar, parazitar infeksiyalar, dori reaksiyalari va boshqa sabablarni klinik holatga qarab ko‘rib chiqish."
        )


    # --------------------------------------------------------
    # PANCYTOPENIA
    # --------------------------------------------------------

    if (
        hb < ranges["Hb"][0]
        and wbc < ranges["WBC"][0]
        and plt < ranges["PLT"][0]
    ):

        findings.append(
            "Eritrotsit, leykotsit va trombotsit qatorlarining birgalikda pasayishi — pansitopeniya patterni."
        )

        recommendations.append(
            "Pansitopeniya sababini aniqlash uchun shifokor nazoratida periferik surtma, retikulotsitlar va zarur qo‘shimcha tekshiruvlarni ko‘rib chiqish."
        )


    # ========================================================
    # RESULTS
    # ========================================================

    if not findings:

        st.markdown("""
        <div class="normal-box">
            🟢 <b>Sezilarli CBC patterni aniqlanmadi.</b><br>
            Kiritilgan ko‘rsatkichlar ushbu prototip reference intervalariga mos.
        </div>
        """, unsafe_allow_html=True)

    else:

        st.markdown("""
        <div class="warning-box">
            🟡 <b>Klinik ahamiyatga ega bo‘lishi mumkin bo‘lgan patternlar mavjud.</b>
        </div>
        """, unsafe_allow_html=True)

        for finding in findings:
            st.write("• " + finding)


        st.markdown(
            '<div class="section-title">💡 Tavsiyalar</div>',
            unsafe_allow_html=True
        )

        for recommendation in recommendations:
            st.write("• " + recommendation)


    # ========================================================
    # CLINICAL CONTEXT
    # ========================================================

    st.markdown(
        '<div class="section-title">🩺 Klinik kontekst</div>',
        unsafe_allow_html=True
    )

    if complaints.strip():

        st.info(
            f"**Bemor shikoyatlari:** {complaints}"
        )

    else:

        st.caption(
            "Klinik shikoyatlar kiritilmagan."
        )


    if diagnosis_context.strip():

        st.info(
            f"**Qo‘shimcha ma’lumot:** {diagnosis_context}"
        )


    # ========================================================
    # OVERALL ASSESSMENT
    # ========================================================

    st.markdown(
        '<div class="section-title">📌 Umumiy baho</div>',
        unsafe_allow_html=True
    )

    if abnormal_count == 0:

        st.success(
            "🟢 Kiritilgan CBC ko‘rsatkichlari prototip reference intervalariga mos."
        )

    elif abnormal_count <= 2:

        st.warning(
            "🟡 Ayrim CBC ko‘rsatkichlarida og‘ish mavjud. "
            "Klinik kontekst bilan birgalikda baholash tavsiya etiladi."
        )

    else:

        st.error(
            "🔴 Bir nechta CBC ko‘rsatkichlarida og‘ish mavjud. "
            "Natijalarni klinik holat, anamnez va laboratoriya reference intervalari bilan birga baholash kerak."
        )


    # ========================================================
    # REPORT DATA
    # ========================================================

    st.markdown(
        '<div class="section-title">📄 Hisobot</div>',
        unsafe_allow_html=True
    )

    report_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    report = f"""
MEDLAB AI DIAGNOSTICS HUB
Professional CBC Clinical Decision Support

Bemor: {patient_name if patient_name else "Ko‘rsatilmagan"}
Yosh: {patient_age}
Jins: {patient_sex}
Sana: {report_time}

CBC NATIJALARI
------------------------------
Gemoglobin: {hb:.1f} g/dL
RBC: {rbc:.2f} ×10¹²/L
Gematokrit: {hct:.1f} %
MCV: {mcv:.1f} fL
MCH: {mch:.1f} pg
MCHC: {mchc:.1f} g/dL
WBC: {wbc:.1f} ×10⁹/L
Neutrofil: {neut:.1f} %
Limfotsit: {lymph:.1f} %
Monotsit: {mono:.1f} %
Eozinofil: {eos:.1f} %
Bazofil: {baso:.1f} %
Trombotsit: {plt:.0f} ×10⁹/L
MPV: {mpv:.1f} fL
RDW-CV: {rdw:.1f} %

HISOBLANGAN KO‘RSATKICHLAR
------------------------------
ANC: {anc:.2f} ×10⁹/L
ALC: {alc:.2f} ×10⁹/L
Neutrofil/Limfotsit: {n_l_ratio:.2f}
Mentzer index: {mentzer:.1f}

KLINIK PATTERNLAR
------------------------------
"""

    if findings:

        for item in findings:
            report += f"- {item}\n"

    else:

        report += "- Sezilarli pattern aniqlanmadi.\n"


    report += """

TAVSIYALAR
------------------------------
"""

    if recommendations:

        for item in recommendations:
            report += f"- {item}\n"

    else:

        report += "- Maxsus tavsiya aniqlanmadi.\n"


    report += """

MUHIM ESLATMA
------------------------------
Ushbu hisobot klinik qarorni qo‘llab-quvvatlovchi prototip
uchun ishlab chiqilgan. Yakuniy tashxis va davolash qarori
malakali shifokor tomonidan, klinik ko‘rik va laboratoriyaning
tasdiqlangan reference intervalari asosida belgilanadi.
"""


    st.download_button(
        label="📥 Hisobotni TXT formatida yuklab olish",
        data=report.encode("utf-8"),
        file_name="MedLab_CBC_Report.txt",
        mime="text/plain",
        use_container_width=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer">
    🧪 <b>MedLab AI Diagnostics Hub</b><br>
    Professional CBC Clinical Decision Support — MVP Prototype<br>
    <span class="small-note">
    Laboratory reference intervals and clinical context must be used for final interpretation.
    </span>
</div>
""", unsafe_allow_html=True)
