import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from PIL import Image
# ============================================================
# MEDLAB AI DIAGNOSTICS HUB
# Professional CBC Clinical Decision Support MVP
# ============================================================

st.set_page_config(
    page_title="MedLab AI Diagnostics",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="collapsed"
)
logo = Image.open("assets/medlab_logo.png.jpg")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.image(logo, width=260)

st.markdown("""
<div style="text-align:center; margin-top:-15px;">
    <h1 style="margin-bottom:5px;">MedLab AI Diagnostics</h1>
    <p style="font-size:18px; color:#4CAF50;">
        AI-assisted Clinical Decision Support
    </p>
</div>
""", unsafe_allow_html=True)# ============================================================
# STYLE
# ============================================================

st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }

    .hero {
        padding: 1.2rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #111827, #1f2937);
        border: 1px solid #374151;
        margin-bottom: 1rem;
    }

    .hero h1 {
        margin-bottom: 0.2rem;
        font-size: 2.2rem;
    }

    .hero p {
        color: #9ca3af;
        font-size: 1rem;
    }

    .normal-box {
        padding: 15px;
        border-radius: 14px;
        background: #064e3b;
        border: 1px solid #10b981;
        color: white;
    }

    .warning-box {
        padding: 15px;
        border-radius: 14px;
        background: #78350f;
        border: 1px solid #f59e0b;
        color: white;
    }

    .danger-box {
        padding: 15px;
        border-radius: 14px;
        background: #7f1d1d;
        border: 1px solid #ef4444;
        color: white;
    }

    .small-note {
        color: #9ca3af;
        font-size: 0.85rem;
    }

    div[data-testid="stMetric"] {
        border: 1px solid #374151;
        padding: 10px;
        border-radius: 12px;
    }

    @media (max-width: 768px) {
        .hero h1 {
            font-size: 1.6rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="hero">
    <h1>🧪 MedLab AI Diagnostics Hub</h1>
    <p>AI-assisted CBC Clinical Decision Support Platform</p>
</div>
""", unsafe_allow_html=True)

st.warning(
    "⚠️ Ushbu tizim klinik qarorni qo‘llab-quvvatlovchi prototipdir. "
    "Natijalar laboratoriyaning o‘z reference intervalari va klinik holat "
    "bilan birgalikda shifokor tomonidan baholanadi."
)

# ============================================================
# PATIENT INFORMATION
# ============================================================

st.header("👤 Bemor ma’lumotlari")

c1, c2, c3 = st.columns(3)

with c1:
    patient_name = st.text_input(
        "Bemor F.I.Sh.",
        placeholder="Ism Familiya"
    )

with c2:
    age = st.number_input(
        "Yosh",
        min_value=0,
        max_value=120,
        value=30,
        step=1
    )

with c3:
    sex = st.selectbox(
        "Jins",
        ["Erkak", "Ayol"]
    )

complaints = st.text_area(
    "Shikoyatlar / klinik ma’lumot",
    placeholder="Masalan: holsizlik, isitma, yo‘tal, bosh aylanishi..."
)

st.divider()

# ============================================================
# REFERENCE RANGE
# ============================================================

def get_reference(age, sex):

    # Adult ranges
    if age >= 18:

        if sex == "Erkak":
            return {
                "Hb": (13.0, 17.0),
                "WBC": (4.0, 10.0),
                "RBC": (4.5, 5.9),
                "PLT": (150, 400),
                "NEU": (40, 75),
                "LYM": (20, 45),
                "MCV": (80, 100),
                "MCH": (27, 33),
                "MCHC": (32, 36),
                "RDW": (11.5, 14.5)
            }

        return {
            "Hb": (12.0, 15.5),
            "WBC": (4.0, 10.0),
            "RBC": (4.0, 5.2),
            "PLT": (150, 400),
            "NEU": (40, 75),
            "LYM": (20, 45),
            "MCV": (80, 100),
            "MCH": (27, 33),
            "MCHC": (32, 36),
            "RDW": (11.5, 14.5)
        }

    # Pediatric simplified prototype ranges
    if age < 1:
        return {
            "Hb": (10.0, 18.0),
            "WBC": (5.0, 19.0),
            "RBC": (3.5, 5.5),
            "PLT": (150, 450),
            "NEU": (15, 45),
            "LYM": (40, 75),
            "MCV": (70, 110),
            "MCH": (23, 37),
            "MCHC": (30, 36),
            "RDW": (11.5, 18)
        }

    if age < 5:
        return {
            "Hb": (11.0, 14.0),
            "WBC": (5.0, 15.0),
            "RBC": (3.9, 5.3),
            "PLT": (150, 450),
            "NEU": (25, 60),
            "LYM": (30, 65),
            "MCV": (70, 86),
            "MCH": (24, 30),
            "MCHC": (31, 36),
            "RDW": (11.5, 15)
        }

    return {
        "Hb": (11.5, 15.0),
        "WBC": (4.5, 13.5),
        "RBC": (4.0, 5.3),
        "PLT": (150, 450),
        "NEU": (30, 65),
        "LYM": (25, 60),
        "MCV": (75, 95),
        "MCH": (25, 32),
        "MCHC": (31, 36),
        "RDW": (11.5, 15)
    }


ref = get_reference(age, sex)

# ============================================================
# CBC INPUT
# ============================================================

st.header("🩸 CBC natijalarini kiriting")

col1, col2 = st.columns(2)

with col1:

    st.subheader("🔴 Eritrotsit qatori")

    hb = st.number_input(
        "Gemoglobin (g/dL)",
        min_value=0.0,
        max_value=30.0,
        value=13.0,
        step=0.1
    )

    rbc = st.number_input(
        "RBC (×10¹²/L)",
        min_value=0.0,
        max_value=10.0,
        value=4.5,
        step=0.1
    )

    mcv = st.number_input(
        "MCV (fL)",
        min_value=0.0,
        max_value=150.0,
        value=90.0,
        step=0.1
    )

    mch = st.number_input(
        "MCH (pg)",
        min_value=0.0,
        max_value=50.0,
        value=30.0,
        step=0.1
    )

    mchc = st.number_input(
        "MCHC (g/dL)",
        min_value=0.0,
        max_value=50.0,
        value=34.0,
        step=0.1
    )

    rdw = st.number_input(
        "RDW (%)",
        min_value=0.0,
        max_value=40.0,
        value=13.0,
        step=0.1
    )

with col2:

    st.subheader("⚪ Leykotsit qatori")

    wbc = st.number_input(
        "WBC (×10⁹/L)",
        min_value=0.0,
        max_value=100.0,
        value=7.0,
        step=0.1
    )

    neut = st.number_input(
        "Neutrofil (%)",
        min_value=0.0,
        max_value=100.0,
        value=55.0,
        step=0.1
    )

    lymph = st.number_input(
        "Limfotsit (%)",
        min_value=0.0,
        max_value=100.0,
        value=35.0,
        step=0.1
    )

    st.subheader("🟣 Trombotsit qatori")

    plt = st.number_input(
        "Trombotsit (×10⁹/L)",
        min_value=0.0,
        max_value=1000.0,
        value=250.0,
        step=1.0
    )

# ============================================================
# ANALYSIS FUNCTIONS
# ============================================================

def flag(value, low, high):
    if value < low:
        return "PAST"
    elif value > high:
        return "YUQORI"
    return "NORMAL"


def flag_icon(status):
    if status == "NORMAL":
        return "🟢"
    if status == "PAST":
        return "🔵"
    return "🔴"


results = {
    "Gemoglobin": {
        "value": hb,
        "unit": "g/dL",
        "range": ref["Hb"],
        "status": flag(hb, *ref["Hb"])
    },
    "RBC": {
        "value": rbc,
        "unit": "×10¹²/L",
        "range": ref["RBC"],
        "status": flag(rbc, *ref["RBC"])
    },
    "MCV": {
        "value": mcv,
        "unit": "fL",
        "range": ref["MCV"],
        "status": flag(mcv, *ref["MCV"])
    },
    "MCH": {
        "value": mch,
        "unit": "pg",
        "range": ref["MCH"],
        "status": flag(mch, *ref["MCH"])
    },
    "MCHC": {
        "value": mchc,
        "unit": "g/dL",
        "range": ref["MCHC"],
        "status": flag(mchc, *ref["MCHC"])
    },
    "RDW": {
        "value": rdw,
        "unit": "%",
        "range": ref["RDW"],
        "status": flag(rdw, *ref["RDW"])
    },
    "WBC": {
        "value": wbc,
        "unit": "×10⁹/L",
        "range": ref["WBC"],
        "status": flag(wbc, *ref["WBC"])
    },
    "Neutrofil": {
        "value": neut,
        "unit": "%",
        "range": ref["NEU"],
        "status": flag(neut, *ref["NEU"])
    },
    "Limfotsit": {
        "value": lymph,
        "unit": "%",
        "range": ref["LYM"],
        "status": flag(lymph, *ref["LYM"])
    },
    "Trombotsit": {
        "value": plt,
        "unit": "×10⁹/L",
        "range": ref["PLT"],
        "status": flag(plt, *ref["PLT"])
    }
}

# ============================================================
# ANALYZE BUTTON
# ============================================================

st.divider()

analyze = st.button(
    "🔬 CBC NI PROFESSIONAL TAHLIL QILISH",
    use_container_width=True,
    type="primary"
)

if analyze:

    # --------------------------------------------------------
    # TABLE
    # --------------------------------------------------------

    st.header("📊 CBC natijalari")

    rows = []

    for name, item in results.items():

        low, high = item["range"]

        rows.append({
            "Ko‘rsatkich": name,
            "Natija": item["value"],
            "Birlik": item["unit"],
            "Reference": f"{low} – {high}",
            "Holat": f"{flag_icon(item['status'])} {item['status']}"
        })

    df = pd.DataFrame(rows)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    abnormal = [
        name for name, item in results.items()
        if item["status"] != "NORMAL"
    ]

    st.header("🧠 Klinik interpretatsiya")

    if len(abnormal) == 0:

        st.markdown("""
        <div class="normal-box">
        <h3>🟢 Sezilarli CBC og‘ishi aniqlanmadi</h3>
        Kiritilgan ko‘rsatkichlar tanlangan yosh va jins uchun
        ishlatilayotgan prototip reference intervalari doirasida.
        </div>
        """, unsafe_allow_html=True)

    else:

        st.markdown(
            f"""
            <div class="warning-box">
            <h3>🟡 E’tibor talab qiluvchi ko‘rsatkichlar: {len(abnormal)}</h3>
            Quyidagi laborator ko‘rsatkichlarda reference intervaldan
            og‘ish aniqlandi.
            </div>
            """,
            unsafe_allow_html=True
        )

        for name in abnormal:

            item = results[name]
            low, high = item["range"]

            if item["status"] == "PAST":

                st.write(
                    f"🔵 **{name} past:** "
                    f"{item['value']} {item['unit']} "
                    f"(reference: {low}–{high})"
                )

            else:

                st.write(
                    f"🔴 **{name} yuqori:** "
                    f"{item['value']} {item['unit']} "
                    f"(reference: {low}–{high})"
                )

    # --------------------------------------------------------
    # CLINICAL PATTERN DETECTION
    # --------------------------------------------------------

    st.subheader("🔎 Ehtimoliy klinik yo‘nalishlar")

    findings = []
    recommendations = []

    # Anemia pattern
    if hb < ref["Hb"][0]:

        findings.append(
            "Gemoglobin kamaygan — anemiya mavjudligini klinik jihatdan baholash kerak."
        )

        if mcv < ref["MCV"][0]:

            findings.append(
                "Hb pasayishi + MCV pastligi mikrotsitar anemiya yo‘nalishini ko‘rsatishi mumkin."
            )

            recommendations.append(
                "Temir almashinuvi: ferritin, transferrin saturation va zarurat bo‘lsa CRP ko‘rib chiqilsin."
            )

        elif mcv > ref["MCV"][1]:

            findings.append(
                "Hb pasayishi + MCV yuqoriligi makrotsitar anemiya yo‘nalishini ko‘rsatishi mumkin."
            )

            recommendations.append(
                "Vitamin B12 va folat holatini klinik vaziyatga qarab baholash."
            )

        else:

            findings.append(
                "Normotsitar anemiya ehtimoli mavjud."
            )

            recommendations.append(
                "Qon yo‘qotilishi, surunkali kasalliklar va boshqa sabablar klinik jihatdan baholansin."
            )

    # Leukocytosis
    if wbc > ref["WBC"][1]:

        findings.append(
            "Leykotsitlar soni yuqori — leykotsitoz."
        )

        recommendations.append(
            "Infeksiya, yallig‘lanish, stress va dori ta’siri klinik belgilar bilan birga baholansin."
        )

    # Leukopenia
    if wbc < ref["WBC"][0]:

        findings.append(
            "Leykotsitlar soni past — leykopeniya."
        )

        recommendations.append(
            "Virusli infeksiyalar, dori ta’siri va boshqa sabablarni klinik vaziyatga qarab baholash."
        )

    # Neutrophilia
    if neut > ref["NEU"][1]:

        findings.append(
            "Neytrofillar ulushi yuqori — neytrofil yo‘nalishdagi o‘zgarish."
        )

    # Neutropenia
    if neut < ref["NEU"][0]:

        findings.append(
            "Neytrofillar ulushi past — neytropeniya ehtimoli."
        )

    # Lymphocytosis
    if lymph > ref["LYM"][1]:

        findings.append(
            "Limfotsitlar ulushi yuqori — limfotsitoz."
        )

    # Thrombocytopenia
    if plt < ref["PLT"][0]:

        findings.append(
            "Trombotsitlar soni past — trombotsitopeniya."
        )

        recommendations.append(
            "Qon ketish belgilari bo‘lsa shoshilinch klinik baholash zarur; "
            "natijani qayta tekshirish va sababini aniqlash ko‘rib chiqilsin."
        )

    # Thrombocytosis
    if plt > ref["PLT"][1]:

        findings.append(
            "Trombotsitlar soni yuqori — trombotsitoz."
        )

        recommendations.append(
            "Reaktiv sabablar, yallig‘lanish va temir tanqisligi klinik vaziyatga qarab baholansin."
        )

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    if not findings:

        st.success(
            "🔬 Kiritilgan CBC ko‘rsatkichlarida ushbu prototip qoidalari "
            "bo‘yicha muhim klinik pattern aniqlanmadi."
        )

    else:

        for finding in findings:
            st.write("• " + finding)

    # --------------------------------------------------------
    # RECOMMENDATIONS
    # --------------------------------------------------------

    st.subheader("💡 Tavsiyalar")

    if recommendations:

        for recommendation in recommendations:
            st.write("• " + recommendation)

    else:

        st.write(
            "• Klinik holat, anamnez va laboratoriyaning o‘z reference "
            "intervalari bilan birgalikda baholash."
        )

    # --------------------------------------------------------
    # OVERALL STATUS
    # --------------------------------------------------------

    st.header("📌 Umumiy baho")

    severe = False

    if plt < 50:
        severe = True

    if hb < 8:
        severe = True

    if wbc < 2 or wbc > 30:
        severe = True

    if severe:

        st.markdown("""
        <div class="danger-box">
        <h3>🔴 Muhim laborator og‘ish</h3>
        Ayrim ko‘rsatkichlar sezilarli darajada o‘zgargan.
        Klinik holatga qarab shifokor tomonidan tezkor baholash talab qilinishi mumkin.
        </div>
        """, unsafe_allow_html=True)

    elif abnormal:

        st.warning(
            "🟡 Laborator ko‘rsatkichlarda og‘ishlar mavjud. "
            "Klinik kontekst bilan birgalikda baholang."
        )

    else:

        st.success(
            "🟢 CBC prototip reference intervalari bo‘yicha sezilarli og‘ishsiz."
        )

    # --------------------------------------------------------
    # PDF REPORT
    # --------------------------------------------------------

    st.divider()
    st.header("📄 Hisobot")

    report_text = f"""
MEDLAB AI DIAGNOSTICS HUB
Professional CBC Clinical Decision Support

Sana: {datetime.now().strftime("%Y-%m-%d %H:%M")}

Bemor: {patient_name or "Ko‘rsatilmagan"}
Yosh: {age}
Jins: {sex}

Klinik ma’lumot:
{complaints or "Ko‘rsatilmagan"}

CBC NATIJALARI
----------------------------------------
"""

    for name, item in results.items():

        low, high = item["range"]

        report_text += (
            f"{name}: {item['value']} {item['unit']} | "
            f"Reference: {low}-{high} | {item['status']}\n"
        )

    report_text += "\nKLINIK INTERPRETATSIYA\n----------------------------------------\n"

    if findings:

        for finding in findings:
            report_text += "- " + finding + "\n"

    else:

        report_text += "- Sezilarli pattern aniqlanmadi.\n"

    report_text += "\nTAVSIYALAR\n----------------------------------------\n"

    for recommendation in recommendations:

        report_text += "- " + recommendation + "\n"

    report_text += """
    
MUHIM:
Ushbu dastur klinik qarorni qo‘llab-quvvatlovchi prototip hisoblanadi.
Yakuniy tashxis va davolash qarori shifokor tomonidan belgilanadi.
Reference intervalari laboratoriya usuliga qarab farq qilishi mumkin.
"""

    pdf_bytes = None

    try:

        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas

        buffer = BytesIO()

        pdf = canvas.Canvas(buffer, pagesize=A4)

        width, height = A4
        y = height - 50

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(
            40,
            y,
            "MedLab AI Diagnostics Hub"
        )

        y -= 30

        pdf.setFont("Helvetica", 9)

        for line in report_text.split("\n"):

            if y < 40:

                pdf.showPage()
                y = height - 50
                pdf.setFont("Helvetica", 9)

            pdf.drawString(
                40,
                y,
                line[:115]
            )

            y -= 13

        pdf.save()

        pdf_bytes = buffer.getvalue()

    except Exception:

        pdf_bytes = None

    if pdf_bytes:

        st.download_button(
            "📥 PDF hisobotni yuklab olish",
            data=pdf_bytes,
            file_name="MedLab_CBC_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    else:

        st.download_button(
            "📥 Hisobotni yuklab olish",
            data=report_text,
            file_name="MedLab_CBC_Report.txt",
            mime="text/plain",
            use_container_width=True
        )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🧪 MedLab AI Diagnostics Hub — Professional CBC Clinical Decision Support MVP"
)

st.caption(
    "Prototype only • Laboratory reference intervals should be verified locally • "
    "Final clinical decisions remain with a qualified healthcare professional."
    )
