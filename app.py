import streamlit as st

st.set_page_config(
    page_title="MedLab AI Diagnostics",
    page_icon="🧪",
    layout="centered"
)

st.title("🧪 MedLab AI Diagnostics Hub")
st.write("AI-assisted CBC laboratory analysis prototype")

st.info(
    "⚠️ Ushbu tizim klinik qarorlarni qo‘llab-quvvatlash uchun "
    "prototip hisoblanadi. Yakuniy tashxisni shifokor belgilaydi."
)

st.header("📋 CBC natijalarini kiriting")

col1, col2 = st.columns(2)

with col1:
    hemoglobin = st.number_input(
        "Gemoglobin (g/dL)", min_value=0.0, value=13.0
    )
    wbc = st.number_input(
        "WBC (×10⁹/L)", min_value=0.0, value=7.0
    )
    platelets = st.number_input(
        "Trombosit (×10⁹/L)", min_value=0.0, value=250.0
    )

with col2:
    rbc = st.number_input(
        "RBC (×10¹²/L)", min_value=0.0, value=4.5
    )
    neutrophils = st.number_input(
        "Neutrofil (%)", min_value=0.0, max_value=100.0, value=55.0
    )
    lymphocytes = st.number_input(
        "Limfotsit (%)", min_value=0.0, max_value=100.0, value=35.0
    )

if st.button("🔍 CBC ni AI yordamida tahlil qilish"):

    findings = []
    recommendations = []
    severity = "Normal"

    # Hemoglobin
    if hemoglobin < 12:
        findings.append("Gemoglobin past")
        recommendations.append("Anemiya ehtimolini baholash kerak")
        severity = "Diqqat"
    elif hemoglobin > 17.5:
        findings.append("Gemoglobin yuqori")
        recommendations.append("Suvsizlanish va boshqa sabablarni baholash kerak")
        severity = "Diqqat"

    # WBC
    if wbc < 4:
        findings.append("Leykotsitlar kamaygan")
        recommendations.append("Leykopeniya sabablarini baholash kerak")
        severity = "Diqqat"
    elif wbc > 10:
        findings.append("Leykotsitlar oshgan")
        recommendations.append("Infeksiya yoki yallig‘lanish belgilarini baholash kerak")
        severity = "Diqqat"

    # Platelets
    if platelets < 150:
        findings.append("Trombositlar kamaygan")
        recommendations.append("Trombositopeniya sabablarini baholash kerak")
        severity = "Diqqat"
    elif platelets > 450:
        findings.append("Trombositlar yuqori")
        recommendations.append("Trombotsitoz sabablarini baholash kerak")
        severity = "Diqqat"

    # Neutrophils
    if neutrophils > 75:
        findings.append("Neutrofil foizi yuqori")
        recommendations.append("Yallig‘lanish yoki bakterial infeksiya ehtimolini klinik baholash")
    elif neutrophils < 40:
        findings.append("Neutrofil foizi past")
        recommendations.append("Neutropeniya ehtimolini baholash")

    # Lymphocytes
    if lymphocytes > 45:
        findings.append("Limfotsitlar foizi yuqori")
        recommendations.append("Virusli infeksiya va boshqa sabablarni klinik baholash")
    elif lymphocytes < 20:
        findings.append("Limfotsitlar foizi past")
        recommendations.append("Limfopeniya sabablarini baholash")

    st.header("📊 Tahlil natijasi")

    if not findings:
        st.success("✅ Kiritilgan ko‘rsatkichlarda sezilarli og‘ish aniqlanmadi.")
    else:
        st.warning("⚠️ E'tibor talab qiluvchi ko‘rsatkichlar mavjud.")

        for finding in findings:
            st.write("•", finding)

        st.subheader("💡 Tavsiyalar")

        for recommendation in recommendations:
            st.write("•", recommendation)

    st.subheader("📌 Umumiy holat")

    if severity == "Normal":
        st.success("Normal diapazonga mos")
    else:
        st.warning("Qo‘shimcha klinik baholash tavsiya etiladi")

    st.caption(
        "MedLab AI Diagnostics Hub — MVP prototype | "
        "Natijalar laboratoriya va klinik kontekst bilan birgalikda baholanadi."
      )
