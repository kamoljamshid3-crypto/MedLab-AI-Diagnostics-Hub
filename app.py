import streamlit as st
import pandas as pd
from groq import Groq
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
# ============================================================
# QO'SHIMCHA TAHLILLAR: SIYDIK VA BIOKIMYO
# ============================================================

st.divider()
st.header("🧪 Qo'shimcha laboratoriya modullari")

analysis_type = st.selectbox(
    "Tahlil turini tanlang",
    [
        "🩸 CBC — Umumiy qon tahlili",
        "🧪 UAT — Umumiy siydik tahlili",
        "🧬 Biokimyoviy qon tahlili"
    ]
)

if analysis_type == "🧪 UAT — Umumiy siydik tahlili":

    st.subheader("🧪 Umumiy siydik tahlili")

    col1, col2 = st.columns(2)

    with col1:
        urine_color = st.selectbox(
            "Rang",
            ["Somon-sariq", "To'q sariq", "Qizil", "Jigarrang", "Rangsiz"]
        )

        urine_clarity = st.selectbox(
            "Shaffoflik",
            ["Shaffof", "Biroz loyqa", "Loyqa"]
        )

        urine_ph = st.number_input(
            "pH",
            min_value=3.0,
            max_value=10.0,
            value=6.0
        )

        urine_density = st.number_input(
            "Nisbiy zichlik",
            min_value=1.000,
            max_value=1.050,
            value=1.020,
            format="%.3f"
        )

    with col2:
        protein = st.selectbox(
            "Oqsil",
            ["Manfiy", "Iz miqdorda", "1+", "2+", "3+"]
        )

        glucose = st.selectbox(
            "Glyukoza",
            ["Manfiy", "Musbat"]
        )

        blood = st.selectbox(
            "Qon/eritrotsit",
            ["Manfiy", "Iz miqdorda", "Musbat"]
        )

        leukocytes = st.number_input(
            "Leykotsitlar (ko'rish maydonida)",
            min_value=0,
            max_value=100,
            value=2
        )

    if st.button("🔍 Siydik tahlilini tahlil qilish"):

        urine_findings = []
        urine_recommendations = []

        if urine_ph < 5.0 or urine_ph > 8.0:
            urine_findings.append("pH me'yoriy diapazondan tashqarida.")
            urine_recommendations.append(
                "Klinik holat va ovqatlanish bilan birgalikda baholash."
            )

        if urine_density < 1.005 or urine_density > 1.030:
            urine_findings.append("Nisbiy zichlik o'zgargan.")
            urine_recommendations.append(
                "Suyuqlik balansi va buyrak faoliyatini baholash."
            )

        if protein != "Manfiy":
            urine_findings.append("Siydikda oqsil aniqlangan.")
            urine_recommendations.append(
                "Proteinuriyani qayta tekshirish va klinik baholash."
            )

        if glucose == "Musbat":
            urine_findings.append("Siydikda glyukoza aniqlangan.")
            urine_recommendations.append(
                "Qon glyukozasi va diabet bo'yicha baholash."
            )

        if blood != "Manfiy":
            urine_findings.append("Siydikda qon/eritrotsit belgisi mavjud.")
            urine_recommendations.append(
                "Siydik cho'kmasi va klinik simptomlarni baholash."
            )

        if leukocytes > 5:
            urine_findings.append("Leykotsitlar ko'paygan.")
            urine_recommendations.append(
                "Siydik yo'llari yallig'lanishi/infeksiyasi ehtimolini baholash."
            )

        # Natijalarni session_state'ga saqlaymiz, aks holda AI tugmasi
        # bosilganda sahifa qayta yuklanib, bu natijalar yo'qolib ketardi.
        st.session_state["urine_findings"] = urine_findings
        st.session_state["urine_recommendations"] = urine_recommendations
        st.session_state["urine_inputs"] = {
            "ph": urine_ph,
            "density": urine_density,
            "protein": protein,
            "glucose": glucose,
            "blood": blood,
            "leukocytes": leukocytes,
        }

    # Tahlil natijalarini (agar mavjud bo'lsa) har doim ko'rsatamiz
    if "urine_findings" in st.session_state:

        urine_findings = st.session_state["urine_findings"]
        urine_recommendations = st.session_state["urine_recommendations"]
        saved_inputs = st.session_state["urine_inputs"]

        st.subheader("📊 UAT tahlil natijasi")

        if not urine_findings:
            st.success(
                "✅ Kiritilgan ko'rsatkichlarda sezilarli og'ish aniqlanmadi."
            )
        else:
            st.warning("⚠️ E'tibor talab qiluvchi ko'rsatkichlar mavjud.")

            for finding in urine_findings:
                st.write("•", finding)

            st.subheader("💡 Tavsiyalar")

            for recommendation in urine_recommendations:
                st.write("•", recommendation)

        # AI tugmasi endi tashqi tugmaning ichida emas — mustaqil ishlaydi
        if st.button("🤖 UAT ni AI yordamida klinik tahlil qilish", key="uat_ai_btn"):

            try:
                client = Groq(
                    api_key=st.secrets["GROQ_API_KEY"]
                )

                urine_context = f"""
Bemorning umumiy siydik tahlili (UAT) natijalari:

pH: {saved_inputs['ph']}
Nisbiy zichlik: {saved_inputs['density']}
Oqsil: {saved_inputs['protein']}
Glyukoza: {saved_inputs['glucose']}
Qon/eritrotsit: {saved_inputs['blood']}
Leykotsitlar: {saved_inputs['leukocytes']} ko'rish maydonida

Tizim tomonidan aniqlangan og'ishlar:
{chr(10).join(urine_findings) if urine_findings else "Sezilarli og'ish aniqlanmadi."}
"""

                with st.spinner("🧠 AI UAT natijalarini klinik tahlil qilmoqda..."):

                    response = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {
                                "role": "user",
                                "content": f"""
Siz MedLab AI Diagnostics klinik qarorlarni qo'llab-quvvatlash tizimisiz.

Quyidagi umumiy siydik tahlili natijalarini klinik nuqtai nazardan
ehtiyotkorlik bilan interpretatsiya qiling.

{urine_context}

Javobni O'ZBEK TILIDA quyidagi tartibda bering:

1. 📊 Umumiy baholash
2. 🔎 Muhim laborator o'zgarishlar
3. 🧩 Ehtimoliy klinik yo'nalishlar
4. 💡 Tavsiya etiladigan keyingi tekshiruvlar
5. 👨‍⚕️ Shifokor uchun qisqa xulosa

Muhim:
- Tashxisni qat'iy tasdiqlamang.
- Faqat laborator natijalar asosida ehtimoliy yo'nalishlarni ko'rsating.
- Bemorning yoshi, jinsi, simptomlari va laboratoriya referenslari hisobga
  olinishi kerakligini ta'kidlang.
- Yakuniy klinik qarorni shifokor qabul qiladi.
"""
                            }
                        ]
                    )

                st.session_state["ai_urine_result"] = response.choices[0].message.content

            except Exception as e:
                st.error(f"❌ AI tahlilida xatolik yuz berdi: {e}")

        # AI natijasini (agar mavjud bo'lsa) doim ko'rsatamiz
        if "ai_urine_result" in st.session_state:

            st.subheader("🤖 MedLab AI — UAT klinik interpretatsiyasi")

            st.markdown(st.session_state["ai_urine_result"])

            st.info(
                "ℹ️ AI xulosasi klinik qarorni qo'llab-quvvatlash uchun "
                "mo'ljallangan. Yakuniy tashxis va davolash qarorini "
                "shifokor belgilaydi."
            )
elif analysis_type == "🧬 Biokimyoviy qon tahlili":

    st.subheader("🧬 Biokimyoviy qon tahlili")

    col1, col2 = st.columns(2)

    with col1:
        glucose_bio = st.number_input(
            "Glyukoza (mmol/L)",
            min_value=0.0,
            value=5.0
        )

        creatinine = st.number_input(
            "Kreatinin (µmol/L)",
            min_value=0.0,
            value=80.0
        )

        urea = st.number_input(
            "Mochevina (mmol/L)",
            min_value=0.0,
            value=5.0
        )

        alt = st.number_input(
            "ALT (U/L)",
            min_value=0.0,
            value=25.0
        )

    with col2:
        ast = st.number_input(
            "AST (U/L)",
            min_value=0.0,
            value=25.0
        )

        bilirubin = st.number_input(
            "Umumiy bilirubin (µmol/L)",
            min_value=0.0,
            value=12.0
        )

        total_protein = st.number_input(
            "Umumiy oqsil (g/L)",
            min_value=0.0,
            value=70.0
        )

        cholesterol = st.number_input(
            "Umumiy xolesterin (mmol/L)",
            min_value=0.0,
            value=4.5
        )

    if st.button("🔍 Biokimyoni AI yordamida tahlil qilish", key="bio_ai_btn"):

        try:
            client = Groq(
                api_key=st.secrets["GROQ_API_KEY"]
            )

            patient_context = f"""
            Bemorning biokimyoviy qon tahlili:

            Glyukoza: {glucose_bio} mmol/L
            Kreatinin: {creatinine} µmol/L
            Mochevina: {urea} mmol/L
            ALT: {alt} U/L
            AST: {ast} U/L
            Umumiy bilirubin: {bilirubin} µmol/L
            Umumiy oqsil: {total_protein} g/L
            Umumiy xolesterin: {cholesterol} mmol/L
            """

            with st.spinner("🧠 AI biokimyoviy tahlilni baholamoqda..."):

                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {
                            "role": "user",
                            "content": f"""
                    Siz MedLab AI Diagnostics klinik qarorlarni
                    qo'llab-quvvatlovchi tizimisiz.

                    Quyidagi biokimyoviy qon tahlilini klinik jihatdan
                    ehtiyotkorlik bilan tahlil qiling.

                    {patient_context}

                    Javobni o'zbek tilida bering.

                    Quyidagi tartibda javob bering:

                    1. 📊 Umumiy baholash
                    2. 🔎 Muhim og'ishlar
                    3. 🧩 Ehtimoliy klinik yo'nalishlar
                    4. 🧪 Tavsiya etiladigan qo'shimcha tekshiruvlar
                    5. 👨‍⚕️ Shifokor uchun qisqa xulosa

                    Har bir natijani birgalikda baholang.
                    Bitta laborator ko'rsatkich asosida yakuniy tashxis
                    qo'ymang.

                    Me'yorlar laboratoriya usuli, bemorning yoshi, jinsi
                    va klinik holatiga qarab farq qilishi mumkin.

                    Tashxisni qat'iy tasdiqlamang va dori buyurishni
                    shifokor o'rniga bajarmang.
                    """
                        }
                    ]
                )

            st.session_state["ai_bio_result"] = response.choices[0].message.content

        except Exception as e:
            st.error(f"❌ AI tahlilida xatolik yuz berdi: {e}")

    if "ai_bio_result" in st.session_state:

        st.subheader("🤖 MedLab AI klinik tahlili")

        st.markdown(st.session_state["ai_bio_result"])

        st.info(
            "ℹ️ AI xulosasi klinik qarorni qo'llab-quvvatlash uchun "
            "mo'ljallangan. Yakuniy tashxis va davolash qarorini "
            "shifokor belgilaydi."
        )

st.caption(
    "⚠️ MedLab AI Diagnostics — klinik qarorlarni qo'llab-quvvatlovchi "
    "MVP prototip. Me'yorlar laboratoriya, yosh, jins va klinik holatga "
    "qarab farq qilishi mumkin. Yakuniy qarorni shifokor qabul qiladi."
)
