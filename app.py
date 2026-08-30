import streamlit as st
import pandas as pd
from datetime import datetime

# ============================================================
# MEDLAB AI DIAGNOSTICS HUB
# Professional CBC Clinical Decision Support MVP
# ============================================================

st.set_page_config(
    page_title="MedLab AI Diagnostics",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- STYLE --------------------

st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: 800;
}
.subtitle {
    color: #6b7280;
    font-size: 18px;
}
.result-card {
    padding: 18px;
    border-radius: 14px;
    margin: 10px 0;
    border: 1px solid #ddd;
}
</style>
""", unsafe_allow_html=True)

# -------------------- HEADER --------------------

st.markdown(
    '<div class="main-title">🧪 MedLab AI Diagnostics Hub</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">AI-assisted CBC Clinical Decision Support</div>',
    unsafe_allow_html=True
)

st.warning(
    "⚠️ Ushbu tizim klinik qarorni qo‘llab-quvvatlovchi prototip. "
    "Yakuniy tashxis va davolash qarori shifokor tomonidan belgilanadi."
)

# -------------------- SESSION --------------------

if "history" not in st.session_state:
    st.session_state.history = []

if "result" not in st.session_state:
    st.session_state.result = None


# ============================================================
# REFERENCE INTERVALS
# ============================================================

def get_reference(age, sex):

    if age < 1:
        return {
            "Hb": (9.5, 14.5, "g/dL"),
            "WBC": (5, 17, "×10⁹/L"),
            "PLT": (150, 450, "×10⁹/L"),
            "RBC": (3.0, 5.0, "×10¹²/L"),
            "MCV": (70, 95, "fL"),
            "MCH": (23, 31, "pg"),
            "Neut": (20, 55, "%"),
            "Lymph": (35, 70, "%"),
            "Eos": (0, 6, "%")
        }

    if age < 5:
        return {
            "Hb": (10.5, 14.5, "g/dL"),
            "WBC": (5, 15, "×10⁹/L"),
            "PLT": (150, 450, "×10⁹/L"),
            "RBC": (3.7, 5.3, "×10¹²/L"),
            "MCV": (70, 86, "fL"),
            "MCH": (23, 30, "pg"),
            "Neut": (25, 60, "%"),
            "Lymph": (30, 65, "%"),
            "Eos": (0, 6, "%")
        }

    if age < 13:
        return {
            "Hb": (11, 15, "g/dL"),
            "WBC": (4.5, 13.5, "×10⁹/L"),
            "PLT": (150, 450, "×10⁹/L"),
            "RBC": (4.0, 5.2, "×10¹²/L"),
            "MCV": (75, 95, "fL"),
            "MCH": (24, 32, "pg"),
            "Neut": (35, 65, "%"),
            "Lymph": (25, 55, "%"),
            "Eos": (0, 6, "%")
        }

    if age < 18:
        return {
            "Hb": (11.5, 16, "g/dL"),
            "WBC": (4.5, 13, "×10⁹/L"),
            "PLT": (150, 450, "×10⁹/L"),
            "RBC": (4.0, 5.5, "×10¹²/L"),
            "MCV": (78, 98, "fL"),
            "MCH": (25, 33, "pg"),
            "Neut": (40, 70, "%"),
            "Lymph": (20, 50, "%"),
            "Eos": (0, 6, "%")
        }

    if sex == "Ayol":
        return {
            "Hb": (12, 16, "g/dL"),
            "WBC": (4, 10, "×10⁹/L"),
            "PLT": (150, 400, "×10⁹/L"),
            "RBC": (3.8, 5.2, "×10¹²/L"),
            "MCV": (80, 100, "fL"),
            "MCH": (27, 33, "pg"),
            "Neut": (40, 75, "%"),
            "Lymph": (20, 45, "%"),
            "Eos": (0, 6, "%")
        }

    return {
        "Hb": (13, 17.5, "g/dL"),
        "WBC": (4, 10, "×10⁹/L"),
        "PLT": (150, 400, "×10⁹/L"),
        "RBC": (4.3, 5.8, "×10¹²/L"),
        "MCV": (80, 100, "fL"),
        "MCH": (27, 33, "pg"),
        "Neut": (40, 75, "%"),
        "Lymph": (20, 45, "%"),
        "Eos": (0, 6, "%")
    }


# ============================================================
# ANALYSIS ENGINE
# ============================================================

def analyze(data, ref, symptoms):

    findings = []
    recommendations = []
    abnormal = []

    for key, value in data.items():

        low, high, unit = ref[key]

        if value < low:
            abnormal.append(key)
            findings.append(
                f"⬇️ {key}: {value:g} {unit} "
                f"(reference {low:g}–{high:g})"
            )

        elif value > high:
            abnormal.append(key)
            findings.append(
                f"⬆️ {key}: {value:g} {unit} "
                f"(reference {low:g}–{high:g})"
            )

    # -------- ANEMIA PATTERNS --------

    if data["Hb"] < ref["Hb"][0]:

        if data["MCV"] < ref["MCV"][0]:
            findings.append(
                "🔎 Pattern: mikrositar anemiya ehtimoli."
            )

            recommendations.append(
                "Ferritin, serum iron va transferrin saturation "
                "kabi temir almashinuvi ko‘rsatkichlarini ko‘rib chiqish."
            )

        elif data["MCV"] > ref["MCV"][1]:
            findings.append(
                "🔎 Pattern: makrositar anemiya ehtimoli."
            )

            recommendations.append(
                "Vitamin B12 va folat holatini klinik kontekstda baholash."
            )

        else:
            findings.append(
                "🔎 Gemoglobin pasaygan — anemiya patterni."
            )

    # -------- INFECTION PATTERNS --------

    if (
        data["WBC"] > ref["WBC"][1]
        and data["Neut"] > ref["Neut"][1]
    ):
        findings.append(
            "🔎 Leukotsitoz + neytrofil ustunligi."
        )

        recommendations.append(
            "Infeksiya yoki yallig‘lanish belgilarini klinik baholash."
        )

    if (
        data["WBC"] > ref["WBC"][1]
        and data["Lymph"] > ref["Lymph"][1]
    ):
        findings.append(
            "🔎 Leukotsitoz + limfotsit ustunligi."
        )

        recommendations.append(
            "Virusli/infeksion sabablarni klinik kontekstda baholash."
        )

    # -------- THROMBOCYTES --------

    if data["PLT"] < 100:

        findings.append(
            "⚠️ Trombotsitlar sezilarli kamaygan."
        )

        recommendations.append(
            "Qon ketish belgilari, CBCni qayta tekshirish "
            "va periferik qon surtmasini klinik baholash."
        )

    if data["PLT"] < 50:

        findings.append(
            "🚨 Trombotsit <50 ×10⁹/L — yuqori e’tibor talab qiladi."
        )

    # -------- EOSINOPHILS --------

    if data["Eos"] > ref["Eos"][1]:

        findings.append(
            "🔎 Eozinofillar yuqori."
        )

        recommendations.append(
            "Allergik, parazitar va boshqa sabablarni "
            "klinik ma’lumotlar bilan baholash."
        )

    # -------- SYMPTOMS --------

    s = symptoms.lower()

    if any(x in s for x in ["isitma", "harorat", "38", "39", "40"]):

        recommendations.append(
            "Isitma mavjud: bemorning umumiy holati va "
            "infeksiya o‘chog‘ini klinik baholash."
        )

    if any(x in s for x in ["ko‘karish", "qon ketish", "burundan qon"]):

        recommendations.append(
            "Qon ketish yoki ko‘karish mavjud bo‘lsa, "
            "trombotsitlar va koagulogramma klinik jihatdan baholanadi."
        )

    # -------- SEVERITY --------

    if data["PLT"] < 50 or data["WBC"] < 2:
        severity = "🔴 Yuqori e’tibor"

    elif len(abnormal) >= 4:
        severity = "🟠 Qo‘shimcha baholash"

    elif len(abnormal) > 0:
        severity = "🟡 Yengil o‘zgarish"

    else:
        severity = "🟢 Normal diapazon"

    if not findings:
        findings.append(
            "✅ Kiritilgan CBC ko‘rsatkichlarida sezilarli og‘ish aniqlanmadi."
        )

    if not recommendations:
        recommendations.append(
            "CBC natijalarini shikoyatlar, anamnez va fizik ko‘rik "
            "bilan birgalikda baholash."
        )

    return findings, recommendations, severity, abnormal


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("👤 Bemor ma’lumotlari")

    name = st.text_input(
        "Bemor ismi",
        placeholder="Ism Familiya"
    )

    age = st.number_input(
        "Yosh",
        min_value=0,
        max_value=120,
        value=30
    )

    sex = st.selectbox(
        "Jins",
        ["Erkak", "Ayol"]
    )

    symptoms = st.text_area(
        "Shikoyatlar / klinik ma’lumot",
        placeholder="Masalan: isitma, holsizlik, yo‘tal..."
    )

    st.divider()

    st.caption(
        "Reference intervalari prototip uchun berilgan. "
        "Klinik tizimda laboratoriyaning o‘z reference intervalari "
        "qo‘llanishi kerak."
    )


# ============================================================
# CBC INPUT
# ============================================================

st.header("🩸 CBC natijalarini kiriting")

ref = get_reference(age, sex)

col1, col2 = st.columns(2)

with col1:

    st.subheader("🔴 Eritrotsit qatori")

    hb = st.number_input(
        "Gemoglobin (g/dL)",
        0.0, 30.0, 13.0, 0.1
    )

    rbc = st.number_input(
        "RBC (×10¹²/L)",
        0.0, 10.0, 4.5, 0.01
    )

    mcv = st.number_input(
        "MCV (fL)",
        0.0, 150.0, 90.0, 0.1
    )

    mch = st.number_input(
        "MCH (pg)",
        0.0, 60.0, 30.0, 0.1
    )


with col2:

    st.subheader("⚪ Leykotsit va trombotsit")

    wbc = st.number_input(
        "WBC (×10⁹/L)",
        0.0, 100.0, 7.0, 0.1
    )

    neut = st.number_input(
        "Neutrofil (%)",
        0.0, 100.0, 55.0, 0.5
    )

    lymph = st.number_input(
        "Limfosit (%)",
        0.0, 100.0, 35.0, 0.5
    )

    eos = st.number_input(
        "Eozinofil (%)",
        0.0, 100.0, 2.0, 0.5
    )

    plt = st.number_input(
        "Trombotsit (×10⁹/L)",
        0.0, 1500.0, 250.0, 1.0
    )


# ============================================================
# ANALYZE BUTTON
# ============================================================

if st.button(
    "🔬 CBC NI AI YORDAMIDA TAHLIL QILISH",
    type="primary",
    use_container_width=True
):

    data = {
        "Hb": hb,
        "WBC": wbc,
        "PLT": plt,
        "RBC": rbc,
        "MCV": mcv,
        "MCH": mch,
        "Neut": neut,
        "Lymph": lymph,
        "Eos": eos
    }

    findings, recommendations, severity, abnormal = analyze(
        data,
        ref,
        symptoms
    )

    result = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "name": name,
        "age": age,
        "sex": sex,
        "data": data,
        "findings": findings,
        "recommendations": recommendations,
        "severity": severity,
        "abnormal": abnormal
    }

    st.session_state.result = result
    st.session_state.history.append(result)


# ============================================================
# RESULT
# ============================================================

if st.session_state.result:

    result = st.session_state.result

    st.divider()

    st.header("📊 Tahlil natijasi")

    st.write(
        f"**Bemor:** {result['name'] or 'Ko‘rsatilmagan'}  \n"
        f"**Yosh:** {result['age']}  \n"
        f"**Jins:** {result['sex']}"
    )

    # Severity
    severity = result["severity"]

    if "Normal" in severity:
        st.success(
            "🟢 Umumiy holat: CBC ko‘rsatkichlari "
            "tanlangan reference diapazonga mos."
        )

    elif "Yengil" in severity:
        st.warning(
            "🟡 Umumiy holat: ayrim laborator o‘zgarishlar mavjud."
        )

    elif "Qo‘shimcha" in severity:
        st.warning(
            "🟠 Bir nechta ko‘rsatkichlarda og‘ish mavjud."
        )

    else:
        st.error(
            "🔴 Yuqori e’tibor talab qiluvchi laborator o‘zgarish mavjud."
        )

    # Metrics
    c1, c2, c3 = st.columns(3)

    c1.metric(
        "CBC ko‘rsatkichlari",
        len(result["data"])
    )

    c2.metric(
        "Normal",
        len(result["data"]) - len(result["abnormal"])
    )

    c3.metric(
        "Og‘ish",
        len(result["abnormal"])
    )

    # Table
    st.subheader("🧾 CBC panel")

    rows = []

    for key, value in result["data"].items():

        low, high, unit = ref[key]

        if value < low:
            status = "⬇️ Past"

        elif value > high:
            status = "⬆️ Yuqori"

        else:
            status = "✅ Normal"

        rows.append({
            "Ko‘rsatkich": key,
            "Natija": value,
            "Birlik": unit,
            "Reference": f"{low:g} – {high:g}",
            "Holat": status
        })

    df = pd.DataFrame(rows)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # Chart
    st.subheader("📈 CBC profili")

    chart = pd.DataFrame({
        "Ko‘rsatkich": list(result["data"].keys()),
        "Natija": list(result["data"].values())
    })

    st.bar_chart(
        chart.set_index("Ko‘rsatkich")
    )

    # Findings
    st.subheader("🔎 Aniqlangan o‘zgarishlar")

    for item in result["findings"]:
        st.markdown(
            f'<div class="result-card">{item}</div>',
            unsafe_allow_html=True
        )

    # Recommendations
    st.subheader("💡 Tavsiyalar")

    for item in result["recommendations"]:
        st.info(item)

    # Report
    report = f"""
MEDLAB AI DIAGNOSTICS HUB
CBC CLINICAL REPORT
==============================

Sana: {result['date']}
Bemor: {result['name'] or 'Ko‘rsatilmagan'}
Yosh: {result['age']}
Jins: {result['sex']}

UMUMIY BAHO:
{result['severity']}

CBC NATIJALARI:
"""

    for key, value in result["data"].items():

        low, high, unit = ref[key]

        report += (
            f"\n{key}: {value:g} {unit} "
            f"(Reference: {low:g}–{high:g})"
        )

    report += "\n\nANIQLANGAN HOLATLAR:\n"

    for item in result["findings"]:
        report += f"\n- {item}"

    report += "\n\nTAVSIYALAR:\n"

    for item in result["recommendations"]:
        report += f"\n- {item}"

    report += """
    
IMPORTANT:
Ushbu hisobot klinik qarorni qo‘llab-quvvatlovchi
prototip tomonidan yaratilgan. Yakuniy tashxis va
davolash qarori malakali tibbiy mutaxassis tomonidan
belgilanadi.
"""

    st.download_button(
        "📄 CBC hisobotini yuklab olish",
        data=report,
        file_name="MedLab_CBC_Report.txt",
        mime="text/plain",
        use_container_width=True
    )


# ============================================================
# HISTORY
# ============================================================

st.divider()

st.header("🗂️ Tahlil tarixi")

if st.session_state.history:

    history = []

    for item in st.session_state.history:

        history.append({
            "Sana": item["date"],
            "Bemor": item["name"] or "—",
            "Yosh": item["age"],
            "Jins": item["sex"],
            "Baho": item["severity"],
            "Og‘ish": len(item["abnormal"])
        })

    st.dataframe(
        pd.DataFrame(history),
        use_container_width=True,
        hide_index=True
    )

    if st.button("🗑️ Tarixni tozalash"):
        st.session_state.history = []
        st.rerun()

else:

    st.caption("Hozircha tahlil tarixi mavjud emas.")


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "MedLab AI Diagnostics Hub — Professional CBC Clinical "
    "Decision-Support MVP | Prototype"
            )
