import streamlit as st
import pandas as pd
from groq import Groq
from datetime import datetime
from io import BytesIO
from PIL import Image
import base64

# ============================================================
# MEDLAB AI DIAGNOSTICS HUB
# Professional CBC Clinical Decision Support MVP
# Multilingual: Uzbek / English / Russian
# ============================================================

TEXT_MODEL = "openai/gpt-oss-120b"
# Groq vision models, tried in order — if the first is unavailable/unauthorized
# on your account, the code automatically falls back to the next one.
# Verify current model access in the Groq console: Settings -> Model Permissions.
VISION_MODELS = ["qwen/qwen3.6-27b", "qwen/qwen3.8-27b"]

# ============================================================
# LANGUAGE / TRANSLATION SYSTEM
# ============================================================

LANGUAGES = {
    "uz": "🇺🇿 O'zbekcha",
    "en": "🇬🇧 English",
    "ru": "🇷🇺 Русский",
}

# Language name used inside AI prompts to tell the model which language to answer in
AI_LANG_NAME = {
    "uz": "UZBEK (O'ZBEK TILIDA)",
    "en": "ENGLISH",
    "ru": "RUSSIAN (НА РУССКОМ ЯЗЫКЕ)",
}

TR = {
    "uz": {
        "page_title": "MedLab AI Diagnostics",
        "app_title": "🧪 MedLab AI Diagnostics Hub",
        "app_subtitle": "AI-assisted CBC Clinical Decision Support Platform",
        "hero_tagline": "AI-assisted Clinical Decision Support",
        "prototype_warning": (
            "⚠️ Ushbu tizim klinik qarorni qo‘llab-quvvatlovchi prototipdir. "
            "Natijalar laboratoriyaning o‘z reference intervalari va klinik holat "
            "bilan birgalikda shifokor tomonidan baholanadi."
        ),
        "language_label": "🌐 Til / Language / Язык",

        "patient_header": "👤 Bemor ma’lumotlari",
        "patient_name": "Bemor F.I.Sh.",
        "patient_name_placeholder": "Ism Familiya",
        "age_label": "Yosh",
        "sex_label": "Jins",
        "sex_male": "Erkak",
        "sex_female": "Ayol",
        "complaints_label": "Shikoyatlar / klinik ma’lumot",
        "complaints_placeholder": "Masalan: holsizlik, isitma, yo‘tal, bosh aylanishi...",
        "not_specified": "Ko‘rsatilmagan",

        "cbc_input_header": "🩸 CBC natijalarini kiriting",
        "erythro_subheader": "🔴 Eritrotsit qatori",
        "hb_label": "Gemoglobin (g/dL)",
        "rbc_label": "RBC (×10¹²/L)",
        "mcv_label": "MCV (fL)",
        "mch_label": "MCH (pg)",
        "mchc_label": "MCHC (g/dL)",
        "rdw_label": "RDW (%)",
        "leuko_subheader": "⚪ Leykotsit qatori",
        "wbc_label": "WBC (×10⁹/L)",
        "neut_label": "Neutrofil (%)",
        "lymph_label": "Limfotsit (%)",
        "plt_subheader": "🟣 Trombotsit qatori",
        "plt_label": "Trombotsit (×10⁹/L)",

        "analyze_button": "🔬 CBC NI PROFESSIONAL TAHLIL QILISH",

        "results_header": "📊 CBC natijalari",
        "col_indicator": "Ko‘rsatkich",
        "col_result": "Natija",
        "col_unit": "Birlik",
        "col_reference": "Reference",
        "col_status": "Holat",
        "status_normal": "NORMAL",
        "status_low": "PAST",
        "status_high": "YUQORI",

        "interpretation_header": "🧠 Klinik interpretatsiya",
        "no_abnormal_title": "🟢 Sezilarli CBC og‘ishi aniqlanmadi",
        "no_abnormal_text": (
            "Kiritilgan ko‘rsatkichlar tanlangan yosh va jins uchun "
            "ishlatilayotgan prototip reference intervallari doirasida."
        ),
        "abnormal_title": "🟡 E’tibor talab qiluvchi ko‘rsatkichlar: {count}",
        "abnormal_text": "Quyidagi laborator ko‘rsatkichlarda reference intervaldan og‘ish aniqlandi.",
        "low_line": "🔵 **{name} past:** {value} {unit} (reference: {low}–{high})",
        "high_line": "🔴 **{name} yuqori:** {value} {unit} (reference: {low}–{high})",

        "pattern_header": "🔎 Ehtimoliy klinik yo‘nalishlar",
        "no_pattern": "🔬 Kiritilgan CBC ko‘rsatkichlarida ushbu prototip qoidalari bo‘yicha muhim klinik pattern aniqlanmadi.",
        "recommendations_header": "💡 Tavsiyalar",
        "recommendations_default": "Klinik holat, anamnez va laboratoriyaning o‘z reference intervallari bilan birgalikda baholash.",

        "overall_header": "📌 Umumiy baho",
        "overall_severe_title": "🔴 Muhim laborator og‘ish",
        "overall_severe_text": (
            "Ayrim ko‘rsatkichlar sezilarli darajada o‘zgargan. "
            "Klinik holatga qarab shifokor tomonidan tezkor baholash talab qilinishi mumkin."
        ),
        "overall_abnormal": "🟡 Laborator ko‘rsatkichlarda og‘ishlar mavjud. Klinik kontekst bilan birgalikda baholang.",
        "overall_normal": "🟢 CBC prototip reference intervallari bo‘yicha sezilarli og‘ishsiz.",

        "ai_extra_header": "🤖 AI yordamida qo'shimcha klinik tahlil",
        "ai_cbc_btn": "🧠 CBC ni AI bilan chuqurroq tahlil qilish",
        "ai_result_header_default": "🤖 AI klinik tahlili",
        "ai_result_note_default": (
            "ℹ️ AI xulosasi klinik qarorni qo'llab-quvvatlash uchun mo'ljallangan. "
            "Yakuniy tashxis va davolash qarorini shifokor belgilaydi."
        ),
        "ai_cbc_result_header": "🤖 MedLab AI — CBC chuqur tahlili",
        "ai_error": "❌ AI tahlilida xatolik yuz berdi: {err}",
        "ai_spinner_cbc": "🧠 AI CBC natijalarini chuqur tahlil qilmoqda...",
        "ai_image_or": "**— yoki CBC blankasining rasmini yuklang —**",
        "ai_image_upload_label": "CBC natija blankasi/varag'ining rasmini yuklang",
        "ai_image_btn": "🤖 Rasm asosida AI tahlil qilish",
        "ai_image_result_header": "🤖 AI — rasm asosidagi tahlil",
        "ai_image_result_note": (
            "ℹ️ AI xulosasi yuklangan tasvir asosida tuzilgan dastlabki, "
            "ehtimoliy izoh hisoblanadi. Rasmiy xulosa va yakuniy tashxis "
            "malakali shifokor tomonidan belgilanadi."
        ),
        "ai_image_uploaded_caption": "Yuklangan tasvir",
        "ai_no_image_warning": "⚠️ Avval rasm yuklang.",
        "ai_vision_spinner": "🧠 AI tasvirni tahlil qilmoqda...",
        "ai_vision_error": "❌ AI vision tahlilida xatolik yuz berdi: {err}",

        "report_header": "📄 Hisobot",
        "report_title": "MEDLAB AI DIAGNOSTICS HUB",
        "report_subtitle": "Professional CBC Clinical Decision Support",
        "report_date": "Sana",
        "report_patient": "Bemor",
        "report_age": "Yosh",
        "report_sex": "Jins",
        "report_clinical_info": "Klinik ma’lumot",
        "report_cbc_results": "CBC NATIJALARI",
        "report_interpretation": "KLINIK INTERPRETATSIYA",
        "report_no_pattern": "Sezilarli pattern aniqlanmadi.",
        "report_recommendations": "TAVSIYALAR",
        "report_footer": (
            "MUHIM:\n"
            "Ushbu dastur klinik qarorni qo‘llab-quvvatlovchi prototip hisoblanadi.\n"
            "Yakuniy tashxis va davolash qarori shifokor tomonidan belgilanadi.\n"
            "Reference intervallari laboratoriya usuliga qarab farq qilishi mumkin."
        ),
        "download_pdf": "📥 PDF hisobotni yuklab olish",
        "download_txt": "📥 Hisobotni yuklab olish",

        "footer_caption": "🧪 MedLab AI Diagnostics Hub — Professional CBC Clinical Decision Support MVP",
        "footer_caption2": (
            "Prototip • Laboratoriya reference intervallari mahalliy sharoitda tekshirilishi kerak • "
            "Yakuniy klinik qarorlar malakali tibbiyot xodimi zimmasida qoladi."
        ),

        "extra_modules_header": "🧪 Qo'shimcha laboratoriya modullari",
        "analysis_type_label": "Tahlil turini tanlang",
        "analysis_cbc": "🩸 CBC — Umumiy qon tahlili",
        "analysis_uat": "🧪 UAT — Umumiy siydik tahlili",
        "analysis_bio": "🧬 Biokimyoviy qon tahlili",
        "analysis_uzi": "🩻 UZI — Ultratovush tekshiruvi",
        "analysis_mrt": "🧠 MRT / MSKT — Tasvir tahlili",

        # UAT
        "uat_subheader": "🧪 Umumiy siydik tahlili",
        "uat_color": "Rang",
        "uat_color_opts": ["Somon-sariq", "To'q sariq", "Qizil", "Jigarrang", "Rangsiz"],
        "uat_clarity": "Shaffoflik",
        "uat_clarity_opts": ["Shaffof", "Biroz loyqa", "Loyqa"],
        "uat_ph": "pH",
        "uat_density": "Nisbiy zichlik",
        "uat_protein": "Oqsil",
        "uat_protein_opts": ["Manfiy", "Iz miqdorda", "1+", "2+", "3+"],
        "uat_glucose": "Glyukoza",
        "uat_glucose_opts": ["Manfiy", "Musbat"],
        "uat_blood": "Qon/eritrotsit",
        "uat_blood_opts": ["Manfiy", "Iz miqdorda", "Musbat"],
        "uat_leukocytes": "Leykotsitlar (ko'rish maydonida)",
        "uat_analyze_btn": "🔍 Siydik tahlilini tahlil qilish",
        "uat_result_header": "📊 UAT tahlil natijasi",
        "uat_no_findings": "✅ Kiritilgan ko'rsatkichlarda sezilarli og'ish aniqlanmadi.",
        "uat_has_findings": "⚠️ E'tibor talab qiluvchi ko'rsatkichlar mavjud.",
        "uat_ai_btn": "🤖 UAT ni AI yordamida klinik tahlil qilish",
        "uat_ai_spinner": "🧠 AI UAT natijalarini klinik tahlil qilmoqda...",
        "uat_ai_result_header": "🤖 MedLab AI — UAT klinik interpretatsiyasi",
        "uat_image_or": "**📷 Yoki UAT blankasining rasmini yuklab AI tahlil qildiring**",
        "uat_image_upload_label": "UAT (umumiy siydik tahlili) blankasining rasmini yuklang",

        # Biochem
        "bio_subheader": "🧬 Biokimyoviy qon tahlili",
        "bio_glucose": "Glyukoza (mmol/L)",
        "bio_creatinine": "Kreatinin (µmol/L)",
        "bio_urea": "Mochevina (mmol/L)",
        "bio_alt": "ALT (U/L)",
        "bio_ast": "AST (U/L)",
        "bio_bilirubin": "Umumiy bilirubin (µmol/L)",
        "bio_protein": "Umumiy oqsil (g/L)",
        "bio_cholesterol": "Umumiy xolesterin (mmol/L)",
        "bio_ai_btn": "🔍 Biokimyoni AI yordamida tahlil qilish",
        "bio_ai_spinner": "🧠 AI biokimyoviy tahlilni baholamoqda...",
        "bio_ai_result_header": "🤖 MedLab AI klinik tahlili",
        "bio_image_or": "**📷 Yoki biokimyo blankasining rasmini yuklab AI tahlil qildiring**",
        "bio_image_upload_label": "Biokimyoviy tahlil blankasining rasmini yuklang",

        # UZI
        "uzi_subheader": "🩻 UZI — Ultratovush tekshiruvi tahlili",
        "input_mode_label": "Ma'lumot kiritish usulini tanlang",
        "mode_text": "📝 Shifokor xulosasi (matn)",
        "mode_image": "🖼️ Tasvir yuklash (rasm)",
        "uzi_area_label": "Tekshiruv sohasi",
        "uzi_area_opts": [
            "Qorin bo'shlig'i UZI", "Buyrak/siydik yo'llari UZI",
            "Ginekologik UZI", "Qalqonsimon bez UZI",
            "Yurak UZI (EXO)", "Ko'krak bezi UZI", "Boshqa"
        ],
        "extra_context_label": "Qo'shimcha kontekst (ixtiyoriy)",
        "extra_context_placeholder": "Masalan: klinik shikoyat, yo'naltirilgan sabab...",
        "uzi_text_area_label": "UZI xulosasi matnini kiriting",
        "uzi_text_placeholder": "Ultratovush tekshiruvi xulosasini shu yerga joylashtiring...",
        "uzi_text_ai_btn": "🤖 UZI xulosasini AI yordamida tahlil qilish",
        "uzi_no_text_warning": "⚠️ Avval UZI xulosasi matnini kiriting.",
        "uzi_text_spinner": "🧠 AI UZI xulosasini tahlil qilmoqda...",
        "uzi_text_result_header": "🤖 MedLab AI — UZI xulosa tahlili",
        "uzi_text_result_note": (
            "ℹ️ AI xulosasi faqat yozilgan matn asosida tuzilgan. "
            "Tasvirning o'zi ko'rilmagan. Yakuniy tashxis va davolash "
            "qarorini shifokor belgilaydi."
        ),
        "uzi_vision_caption": (
            "⚠️ Diqqat: bu vision-AI modeli, sonograf emas. Model faqat "
            "ko'rinadigan tasvir asosida ehtimoliy izohlar beradi."
        ),
        "uzi_image_upload_label": "UZI tasvirini yuklang (JPG, PNG)",

        # MRT
        "mrt_subheader": "🧠 MRT / MSKT — Tasvir tahlili",
        "mrt_mode_text": "📝 Radiolog xulosasi (matn)",
        "mrt_mode_image": "🖼️ Tasvir yuklash (rasm)",
        "mrt_scan_type_label": "Tekshiruv turi",
        "mrt_scan_type_opts": [
            "Bosh miya MRT", "Umurtqa pog'onasi MRT", "Bo'g'im MRT",
            "Qorin bo'shlig'i MSKT", "Ko'krak qafasi MSKT",
            "Bosh miya MSKT", "Boshqa"
        ],
        "mrt_context_placeholder": "Masalan: kontrast bilan, klinik shikoyat, yo'naltirilgan sabab...",
        "mrt_text_area_label": "Radiolog xulosasi matnini kiriting",
        "mrt_text_placeholder": "Radiolog tomonidan yozilgan tasvir tavsifi / xulosani shu yerga joylashtiring...",
        "mrt_text_ai_btn": "🤖 Xulosani AI yordamida klinik tahlil qilish",
        "mrt_no_text_warning": "⚠️ Avval radiolog xulosasi matnini kiriting.",
        "mrt_text_spinner": "🧠 AI tasvir xulosasini klinik tahlil qilmoqda...",
        "mrt_text_result_header": "🤖 MedLab AI — MRT/MSKT xulosa tahlili",
        "mrt_text_result_note": (
            "ℹ️ AI xulosasi faqat radiolog tomonidan yozilgan matn asosida "
            "tuzilgan. Tasvirning o'zi ko'rilmagan. Yakuniy tashxis va "
            "davolash qarorini shifokor belgilaydi."
        ),
        "mrt_image_upload_label": "MRT/MSKT tasvirini yuklang (JPG, PNG)",
        "mrt_vision_caption": (
            "⚠️ Diqqat: bu vision-AI modeli, radiolog emas. DICOM fayllarni "
            "avval JPG/PNG formatiga o'tkazish kerak. Model faqat "
            "ko'rinadigan tasvir asosida ehtimoliy izohlar beradi."
        ),
        "mrt_image_ai_btn": "🤖 Tasvirni AI vision yordamida tahlil qilish",
        "mrt_no_image_warning": "⚠️ Avval tasvir faylini yuklang.",
        "mrt_vision_spinner": "🧠 AI tasvirni vision orqali tahlil qilmoqda...",
        "mrt_vision_error": (
            "❌ AI vision tahlilida xatolik yuz berdi: {err}\n\n"
            "Eslatma: Groq'ning vision modeli nomi vaqt o'tishi bilan "
            "o'zgarishi mumkin — Groq konsolidan joriy model nomini "
            "tekshiring va kerak bo'lsa kodda yangilang."
        ),
        "mrt_image_result_header": "🤖 MedLab AI — MRT/MSKT tasvir tahlili",
        "mrt_image_result_note": (
            "ℹ️ AI vision xulosasi faqat yuklangan tasvir asosida tuzilgan "
            "dastlabki, ehtimoliy izoh hisoblanadi. Rasmiy radiologik "
            "xulosa va yakuniy tashxis malakali shifokor tomonidan "
            "belgilanadi."
        ),

        "final_footer": (
            "⚠️ MedLab AI Diagnostics — klinik qarorlarni qo'llab-quvvatlovchi "
            "MVP prototip. Me'yorlar laboratoriya, yosh, jins va klinik holatga "
            "qarab farq qilishi mumkin. Yakuniy qarorni shifokor qabul qiladi."
        ),
    },

    "en": {
        "page_title": "MedLab AI Diagnostics",
        "app_title": "🧪 MedLab AI Diagnostics Hub",
        "app_subtitle": "AI-assisted CBC Clinical Decision Support Platform",
        "hero_tagline": "AI-assisted Clinical Decision Support",
        "prototype_warning": (
            "⚠️ This system is a clinical decision support prototype. "
            "Results should be evaluated by a physician together with the "
            "laboratory's own reference ranges and the patient's clinical picture."
        ),
        "language_label": "🌐 Til / Language / Язык",

        "patient_header": "👤 Patient Information",
        "patient_name": "Patient Full Name",
        "patient_name_placeholder": "First Last",
        "age_label": "Age",
        "sex_label": "Sex",
        "sex_male": "Male",
        "sex_female": "Female",
        "complaints_label": "Complaints / clinical information",
        "complaints_placeholder": "e.g. fatigue, fever, cough, dizziness...",
        "not_specified": "Not specified",

        "cbc_input_header": "🩸 Enter CBC Results",
        "erythro_subheader": "🔴 Erythrocyte panel",
        "hb_label": "Hemoglobin (g/dL)",
        "rbc_label": "RBC (×10¹²/L)",
        "mcv_label": "MCV (fL)",
        "mch_label": "MCH (pg)",
        "mchc_label": "MCHC (g/dL)",
        "rdw_label": "RDW (%)",
        "leuko_subheader": "⚪ Leukocyte panel",
        "wbc_label": "WBC (×10⁹/L)",
        "neut_label": "Neutrophils (%)",
        "lymph_label": "Lymphocytes (%)",
        "plt_subheader": "🟣 Platelet panel",
        "plt_label": "Platelets (×10⁹/L)",

        "analyze_button": "🔬 RUN PROFESSIONAL CBC ANALYSIS",

        "results_header": "📊 CBC Results",
        "col_indicator": "Indicator",
        "col_result": "Result",
        "col_unit": "Unit",
        "col_reference": "Reference",
        "col_status": "Status",
        "status_normal": "NORMAL",
        "status_low": "LOW",
        "status_high": "HIGH",

        "interpretation_header": "🧠 Clinical Interpretation",
        "no_abnormal_title": "🟢 No significant CBC deviation detected",
        "no_abnormal_text": (
            "The entered values fall within the prototype reference "
            "ranges for the selected age and sex."
        ),
        "abnormal_title": "🟡 Indicators needing attention: {count}",
        "abnormal_text": "The following laboratory indicators deviate from the reference range.",
        "low_line": "🔵 **{name} low:** {value} {unit} (reference: {low}–{high})",
        "high_line": "🔴 **{name} high:** {value} {unit} (reference: {low}–{high})",

        "pattern_header": "🔎 Possible clinical directions",
        "no_pattern": "🔬 No significant clinical pattern was detected in the entered CBC values under this prototype's rules.",
        "recommendations_header": "💡 Recommendations",
        "recommendations_default": "Evaluate together with the clinical picture, history, and the laboratory's own reference ranges.",

        "overall_header": "📌 Overall Assessment",
        "overall_severe_title": "🔴 Significant laboratory deviation",
        "overall_severe_text": (
            "Some indicators have changed significantly. Depending on the "
            "clinical picture, urgent physician evaluation may be required."
        ),
        "overall_abnormal": "🟡 There are deviations in laboratory indicators. Evaluate together with the clinical context.",
        "overall_normal": "🟢 No significant deviation from the CBC prototype reference ranges.",

        "ai_extra_header": "🤖 Additional AI-assisted clinical analysis",
        "ai_cbc_btn": "🧠 Analyze CBC more deeply with AI",
        "ai_result_header_default": "🤖 AI clinical analysis",
        "ai_result_note_default": (
            "ℹ️ The AI summary is intended to support clinical decision-making. "
            "The final diagnosis and treatment decision are made by a physician."
        ),
        "ai_cbc_result_header": "🤖 MedLab AI — In-depth CBC analysis",
        "ai_error": "❌ An error occurred during AI analysis: {err}",
        "ai_spinner_cbc": "🧠 AI is analyzing the CBC results in depth...",
        "ai_image_or": "**— or upload an image of the CBC form —**",
        "ai_image_upload_label": "Upload an image of the CBC result form/sheet",
        "ai_image_btn": "🤖 Analyze with AI based on image",
        "ai_image_result_header": "🤖 AI — image-based analysis",
        "ai_image_result_note": (
            "ℹ️ The AI summary is a preliminary, probabilistic interpretation "
            "based on the uploaded image. The official conclusion and final "
            "diagnosis are determined by a qualified physician."
        ),
        "ai_image_uploaded_caption": "Uploaded image",
        "ai_no_image_warning": "⚠️ Please upload an image first.",
        "ai_vision_spinner": "🧠 AI is analyzing the image...",
        "ai_vision_error": "❌ An error occurred during AI vision analysis: {err}",

        "report_header": "📄 Report",
        "report_title": "MEDLAB AI DIAGNOSTICS HUB",
        "report_subtitle": "Professional CBC Clinical Decision Support",
        "report_date": "Date",
        "report_patient": "Patient",
        "report_age": "Age",
        "report_sex": "Sex",
        "report_clinical_info": "Clinical information",
        "report_cbc_results": "CBC RESULTS",
        "report_interpretation": "CLINICAL INTERPRETATION",
        "report_no_pattern": "No significant pattern detected.",
        "report_recommendations": "RECOMMENDATIONS",
        "report_footer": (
            "IMPORTANT:\n"
            "This program is a clinical decision support prototype.\n"
            "The final diagnosis and treatment decision are made by a physician.\n"
            "Reference ranges may vary depending on the laboratory method."
        ),
        "download_pdf": "📥 Download PDF report",
        "download_txt": "📥 Download report",

        "footer_caption": "🧪 MedLab AI Diagnostics Hub — Professional CBC Clinical Decision Support MVP",
        "footer_caption2": (
            "Prototype only • Laboratory reference intervals should be verified locally • "
            "Final clinical decisions remain with a qualified healthcare professional."
        ),

        "extra_modules_header": "🧪 Additional laboratory modules",
        "analysis_type_label": "Select analysis type",
        "analysis_cbc": "🩸 CBC — Complete Blood Count",
        "analysis_uat": "🧪 Urinalysis (UAT)",
        "analysis_bio": "🧬 Blood biochemistry",
        "analysis_uzi": "🩻 Ultrasound (US)",
        "analysis_mrt": "🧠 MRI / CT — Image analysis",

        # UAT
        "uat_subheader": "🧪 Urinalysis (general urine test)",
        "uat_color": "Color",
        "uat_color_opts": ["Straw-yellow", "Dark yellow", "Red", "Brown", "Colorless"],
        "uat_clarity": "Clarity",
        "uat_clarity_opts": ["Clear", "Slightly cloudy", "Cloudy"],
        "uat_ph": "pH",
        "uat_density": "Specific gravity",
        "uat_protein": "Protein",
        "uat_protein_opts": ["Negative", "Trace", "1+", "2+", "3+"],
        "uat_glucose": "Glucose",
        "uat_glucose_opts": ["Negative", "Positive"],
        "uat_blood": "Blood/erythrocytes",
        "uat_blood_opts": ["Negative", "Trace", "Positive"],
        "uat_leukocytes": "Leukocytes (per field of view)",
        "uat_analyze_btn": "🔍 Analyze urinalysis",
        "uat_result_header": "📊 Urinalysis result",
        "uat_no_findings": "✅ No significant deviation detected in the entered indicators.",
        "uat_has_findings": "⚠️ There are indicators that need attention.",
        "uat_ai_btn": "🤖 Analyze urinalysis clinically with AI",
        "uat_ai_spinner": "🧠 AI is clinically analyzing the urinalysis results...",
        "uat_ai_result_header": "🤖 MedLab AI — Urinalysis clinical interpretation",
        "uat_image_or": "**📷 Or upload an image of the urinalysis form for AI analysis**",
        "uat_image_upload_label": "Upload an image of the urinalysis (UAT) form",

        # Biochem
        "bio_subheader": "🧬 Blood biochemistry",
        "bio_glucose": "Glucose (mmol/L)",
        "bio_creatinine": "Creatinine (µmol/L)",
        "bio_urea": "Urea (mmol/L)",
        "bio_alt": "ALT (U/L)",
        "bio_ast": "AST (U/L)",
        "bio_bilirubin": "Total bilirubin (µmol/L)",
        "bio_protein": "Total protein (g/L)",
        "bio_cholesterol": "Total cholesterol (mmol/L)",
        "bio_ai_btn": "🔍 Analyze biochemistry with AI",
        "bio_ai_spinner": "🧠 AI is evaluating the biochemistry results...",
        "bio_ai_result_header": "🤖 MedLab AI clinical analysis",
        "bio_image_or": "**📷 Or upload an image of the biochemistry form for AI analysis**",
        "bio_image_upload_label": "Upload an image of the biochemistry test form",

        # UZI
        "uzi_subheader": "🩻 Ultrasound examination analysis",
        "input_mode_label": "Choose how to enter data",
        "mode_text": "📝 Physician's report (text)",
        "mode_image": "🖼️ Upload image",
        "uzi_area_label": "Examination area",
        "uzi_area_opts": [
            "Abdominal ultrasound", "Kidney/urinary tract ultrasound",
            "Gynecological ultrasound", "Thyroid ultrasound",
            "Cardiac ultrasound (echo)", "Breast ultrasound", "Other"
        ],
        "extra_context_label": "Additional context (optional)",
        "extra_context_placeholder": "e.g. clinical complaint, reason for referral...",
        "uzi_text_area_label": "Enter the ultrasound report text",
        "uzi_text_placeholder": "Paste the ultrasound examination report here...",
        "uzi_text_ai_btn": "🤖 Analyze ultrasound report with AI",
        "uzi_no_text_warning": "⚠️ Please enter the ultrasound report text first.",
        "uzi_text_spinner": "🧠 AI is analyzing the ultrasound report...",
        "uzi_text_result_header": "🤖 MedLab AI — Ultrasound report analysis",
        "uzi_text_result_note": (
            "ℹ️ The AI summary is based only on the written report. The "
            "image itself was not reviewed. The final diagnosis and "
            "treatment decision are made by a physician."
        ),
        "uzi_vision_caption": (
            "⚠️ Note: this is a vision-AI model, not a sonographer. The model "
            "provides only probabilistic commentary based on the visible image."
        ),
        "uzi_image_upload_label": "Upload the ultrasound image (JPG, PNG)",

        # MRT
        "mrt_subheader": "🧠 MRI / CT — Image analysis",
        "mrt_mode_text": "📝 Radiologist's report (text)",
        "mrt_mode_image": "🖼️ Upload image",
        "mrt_scan_type_label": "Examination type",
        "mrt_scan_type_opts": [
            "Brain MRI", "Spine MRI", "Joint MRI",
            "Abdominal CT", "Chest CT",
            "Brain CT", "Other"
        ],
        "mrt_context_placeholder": "e.g. with contrast, clinical complaint, reason for referral...",
        "mrt_text_area_label": "Enter the radiologist's report text",
        "mrt_text_placeholder": "Paste the radiologist's image description / report here...",
        "mrt_text_ai_btn": "🤖 Analyze report clinically with AI",
        "mrt_no_text_warning": "⚠️ Please enter the radiologist's report text first.",
        "mrt_text_spinner": "🧠 AI is clinically analyzing the imaging report...",
        "mrt_text_result_header": "🤖 MedLab AI — MRI/CT report analysis",
        "mrt_text_result_note": (
            "ℹ️ The AI summary is based only on the text written by the "
            "radiologist. The image itself was not reviewed. The final "
            "diagnosis and treatment decision are made by a physician."
        ),
        "mrt_image_upload_label": "Upload the MRI/CT image (JPG, PNG)",
        "mrt_vision_caption": (
            "⚠️ Note: this is a vision-AI model, not a radiologist. DICOM "
            "files must first be converted to JPG/PNG. The model provides "
            "only probabilistic commentary based on the visible image."
        ),
        "mrt_image_ai_btn": "🤖 Analyze image with AI vision",
        "mrt_no_image_warning": "⚠️ Please upload an image file first.",
        "mrt_vision_spinner": "🧠 AI is analyzing the image via vision...",
        "mrt_vision_error": (
            "❌ An error occurred during AI vision analysis: {err}\n\n"
            "Note: Groq's vision model name may change over time — check "
            "the current model name in the Groq console and update the code if needed."
        ),
        "mrt_image_result_header": "🤖 MedLab AI — MRI/CT image analysis",
        "mrt_image_result_note": (
            "ℹ️ The AI vision summary is a preliminary, probabilistic "
            "interpretation based on the uploaded image. The official "
            "radiological report and final diagnosis are determined by "
            "a qualified physician."
        ),

        "final_footer": (
            "⚠️ MedLab AI Diagnostics — a clinical decision support MVP "
            "prototype. Normal ranges may vary by laboratory, age, sex, "
            "and clinical status. The final decision is made by a physician."
        ),
    },

    "ru": {
        "page_title": "MedLab AI Diagnostics",
        "app_title": "🧪 MedLab AI Diagnostics Hub",
        "app_subtitle": "Платформа поддержки клинических решений на основе ОАК с ИИ",
        "hero_tagline": "Поддержка клинических решений с помощью ИИ",
        "prototype_warning": (
            "⚠️ Данная система является прототипом поддержки клинических решений. "
            "Результаты должны оцениваться врачом с учётом референсных значений "
            "лаборатории и клинической картины пациента."
        ),
        "language_label": "🌐 Til / Language / Язык",

        "patient_header": "👤 Информация о пациенте",
        "patient_name": "Ф.И.О. пациента",
        "patient_name_placeholder": "Имя Фамилия",
        "age_label": "Возраст",
        "sex_label": "Пол",
        "sex_male": "Мужской",
        "sex_female": "Женский",
        "complaints_label": "Жалобы / клиническая информация",
        "complaints_placeholder": "Например: слабость, повышение температуры, кашель, головокружение...",
        "not_specified": "Не указано",

        "cbc_input_header": "🩸 Введите результаты ОАК",
        "erythro_subheader": "🔴 Эритроцитарный ряд",
        "hb_label": "Гемоглобин (г/дл)",
        "rbc_label": "RBC (×10¹²/л)",
        "mcv_label": "MCV (фл)",
        "mch_label": "MCH (пг)",
        "mchc_label": "MCHC (г/дл)",
        "rdw_label": "RDW (%)",
        "leuko_subheader": "⚪ Лейкоцитарный ряд",
        "wbc_label": "WBC (×10⁹/л)",
        "neut_label": "Нейтрофилы (%)",
        "lymph_label": "Лимфоциты (%)",
        "plt_subheader": "🟣 Тромбоцитарный ряд",
        "plt_label": "Тромбоциты (×10⁹/л)",

        "analyze_button": "🔬 ВЫПОЛНИТЬ ПРОФЕССИОНАЛЬНЫЙ АНАЛИЗ ОАК",

        "results_header": "📊 Результаты ОАК",
        "col_indicator": "Показатель",
        "col_result": "Результат",
        "col_unit": "Единица",
        "col_reference": "Референс",
        "col_status": "Статус",
        "status_normal": "НОРМА",
        "status_low": "НИЖЕ НОРМЫ",
        "status_high": "ВЫШЕ НОРМЫ",

        "interpretation_header": "🧠 Клиническая интерпретация",
        "no_abnormal_title": "🟢 Значимых отклонений ОАК не обнаружено",
        "no_abnormal_text": (
            "Введённые показатели находятся в пределах прототипных "
            "референсных диапазонов для выбранного возраста и пола."
        ),
        "abnormal_title": "🟡 Показатели, требующие внимания: {count}",
        "abnormal_text": "В следующих лабораторных показателях выявлено отклонение от референсного диапазона.",
        "low_line": "🔵 **{name} снижен(а):** {value} {unit} (референс: {low}–{high})",
        "high_line": "🔴 **{name} повышен(а):** {value} {unit} (референс: {low}–{high})",

        "pattern_header": "🔎 Возможные клинические направления",
        "no_pattern": "🔬 По правилам данного прототипа значимого клинического паттерна во введённых показателях ОАК не выявлено.",
        "recommendations_header": "💡 Рекомендации",
        "recommendations_default": "Оценивать совместно с клинической картиной, анамнезом и собственными референсными диапазонами лаборатории.",

        "overall_header": "📌 Общая оценка",
        "overall_severe_title": "🔴 Значимое лабораторное отклонение",
        "overall_severe_text": (
            "Некоторые показатели изменены значительно. В зависимости от "
            "клинической картины может потребоваться срочная оценка врачом."
        ),
        "overall_abnormal": "🟡 Имеются отклонения в лабораторных показателях. Оценивайте с учётом клинического контекста.",
        "overall_normal": "🟢 Значимых отклонений от прототипных референсных диапазонов ОАК не выявлено.",

        "ai_extra_header": "🤖 Дополнительный клинический анализ с помощью ИИ",
        "ai_cbc_btn": "🧠 Провести углублённый анализ ОАК с помощью ИИ",
        "ai_result_header_default": "🤖 Клинический анализ ИИ",
        "ai_result_note_default": (
            "ℹ️ Заключение ИИ предназначено для поддержки клинического решения. "
            "Окончательный диагноз и решение о лечении принимает врач."
        ),
        "ai_cbc_result_header": "🤖 MedLab AI — углублённый анализ ОАК",
        "ai_error": "❌ Произошла ошибка при анализе ИИ: {err}",
        "ai_spinner_cbc": "🧠 ИИ проводит углублённый анализ результатов ОАК...",
        "ai_image_or": "**— или загрузите фото бланка ОАК —**",
        "ai_image_upload_label": "Загрузите фото бланка/листа результатов ОАК",
        "ai_image_btn": "🤖 Анализировать с помощью ИИ по изображению",
        "ai_image_result_header": "🤖 ИИ — анализ по изображению",
        "ai_image_result_note": (
            "ℹ️ Заключение ИИ является предварительным, вероятностным "
            "толкованием на основе загруженного изображения. Официальное "
            "заключение и окончательный диагноз определяет квалифицированный врач."
        ),
        "ai_image_uploaded_caption": "Загруженное изображение",
        "ai_no_image_warning": "⚠️ Сначала загрузите изображение.",
        "ai_vision_spinner": "🧠 ИИ анализирует изображение...",
        "ai_vision_error": "❌ Произошла ошибка при анализе ИИ vision: {err}",

        "report_header": "📄 Отчёт",
        "report_title": "MEDLAB AI DIAGNOSTICS HUB",
        "report_subtitle": "Профессиональная поддержка клинических решений по ОАК",
        "report_date": "Дата",
        "report_patient": "Пациент",
        "report_age": "Возраст",
        "report_sex": "Пол",
        "report_clinical_info": "Клиническая информация",
        "report_cbc_results": "РЕЗУЛЬТАТЫ ОАК",
        "report_interpretation": "КЛИНИЧЕСКАЯ ИНТЕРПРЕТАЦИЯ",
        "report_no_pattern": "Значимого паттерна не выявлено.",
        "report_recommendations": "РЕКОМЕНДАЦИИ",
        "report_footer": (
            "ВАЖНО:\n"
            "Данная программа является прототипом поддержки клинических решений.\n"
            "Окончательный диагноз и решение о лечении принимает врач.\n"
            "Референсные диапазоны могут отличаться в зависимости от метода лаборатории."
        ),
        "download_pdf": "📥 Скачать PDF-отчёт",
        "download_txt": "📥 Скачать отчёт",

        "footer_caption": "🧪 MedLab AI Diagnostics Hub — прототип MVP поддержки клинических решений по ОАК",
        "footer_caption2": (
            "Только прототип • Референсные интервалы лаборатории необходимо проверять локально • "
            "Окончательные клинические решения остаются за квалифицированным медицинским специалистом."
        ),

        "extra_modules_header": "🧪 Дополнительные лабораторные модули",
        "analysis_type_label": "Выберите тип анализа",
        "analysis_cbc": "🩸 ОАК — общий анализ крови",
        "analysis_uat": "🧪 ОАМ — общий анализ мочи",
        "analysis_bio": "🧬 Биохимический анализ крови",
        "analysis_uzi": "🩻 УЗИ — ультразвуковое исследование",
        "analysis_mrt": "🧠 МРТ / КТ — анализ изображения",

        # UAT
        "uat_subheader": "🧪 Общий анализ мочи",
        "uat_color": "Цвет",
        "uat_color_opts": ["Соломенно-жёлтый", "Тёмно-жёлтый", "Красный", "Коричневый", "Бесцветный"],
        "uat_clarity": "Прозрачность",
        "uat_clarity_opts": ["Прозрачная", "Слегка мутная", "Мутная"],
        "uat_ph": "pH",
        "uat_density": "Относительная плотность",
        "uat_protein": "Белок",
        "uat_protein_opts": ["Отрицательно", "Следы", "1+", "2+", "3+"],
        "uat_glucose": "Глюкоза",
        "uat_glucose_opts": ["Отрицательно", "Положительно"],
        "uat_blood": "Кровь/эритроциты",
        "uat_blood_opts": ["Отрицательно", "Следы", "Положительно"],
        "uat_leukocytes": "Лейкоциты (в поле зрения)",
        "uat_analyze_btn": "🔍 Проанализировать анализ мочи",
        "uat_result_header": "📊 Результат ОАМ",
        "uat_no_findings": "✅ Значимых отклонений во введённых показателях не обнаружено.",
        "uat_has_findings": "⚠️ Есть показатели, требующие внимания.",
        "uat_ai_btn": "🤖 Провести клинический анализ ОАМ с помощью ИИ",
        "uat_ai_spinner": "🧠 ИИ проводит клинический анализ результатов ОАМ...",
        "uat_ai_result_header": "🤖 MedLab AI — клиническая интерпретация ОАМ",
        "uat_image_or": "**📷 Или загрузите фото бланка ОАМ для анализа ИИ**",
        "uat_image_upload_label": "Загрузите фото бланка общего анализа мочи (ОАМ)",

        # Biochem
        "bio_subheader": "🧬 Биохимический анализ крови",
        "bio_glucose": "Глюкоза (ммоль/л)",
        "bio_creatinine": "Креатинин (мкмоль/л)",
        "bio_urea": "Мочевина (ммоль/л)",
        "bio_alt": "АЛТ (Ед/л)",
        "bio_ast": "АСТ (Ед/л)",
        "bio_bilirubin": "Общий билирубин (мкмоль/л)",
        "bio_protein": "Общий белок (г/л)",
        "bio_cholesterol": "Общий холестерин (ммоль/л)",
        "bio_ai_btn": "🔍 Проанализировать биохимию с помощью ИИ",
        "bio_ai_spinner": "🧠 ИИ оценивает результаты биохимического анализа...",
        "bio_ai_result_header": "🤖 Клинический анализ MedLab AI",
        "bio_image_or": "**📷 Или загрузите фото бланка биохимии для анализа ИИ**",
        "bio_image_upload_label": "Загрузите фото бланка биохимического анализа",

        # UZI
        "uzi_subheader": "🩻 Анализ ультразвукового исследования",
        "input_mode_label": "Выберите способ ввода данных",
        "mode_text": "📝 Заключение врача (текст)",
        "mode_image": "🖼️ Загрузить изображение",
        "uzi_area_label": "Область исследования",
        "uzi_area_opts": [
            "УЗИ брюшной полости", "УЗИ почек/мочевыводящих путей",
            "Гинекологическое УЗИ", "УЗИ щитовидной железы",
            "УЗИ сердца (ЭхоКГ)", "УЗИ молочной железы", "Другое"
        ],
        "extra_context_label": "Дополнительный контекст (необязательно)",
        "extra_context_placeholder": "Например: клиническая жалоба, причина направления...",
        "uzi_text_area_label": "Введите текст заключения УЗИ",
        "uzi_text_placeholder": "Вставьте сюда заключение ультразвукового исследования...",
        "uzi_text_ai_btn": "🤖 Проанализировать заключение УЗИ с помощью ИИ",
        "uzi_no_text_warning": "⚠️ Сначала введите текст заключения УЗИ.",
        "uzi_text_spinner": "🧠 ИИ анализирует заключение УЗИ...",
        "uzi_text_result_header": "🤖 MedLab AI — анализ заключения УЗИ",
        "uzi_text_result_note": (
            "ℹ️ Заключение ИИ основано только на письменном тексте. Само "
            "изображение не рассматривалось. Окончательный диагноз и "
            "решение о лечении принимает врач."
        ),
        "uzi_vision_caption": (
            "⚠️ Внимание: это модель vision-AI, а не сонограф. Модель даёт "
            "только вероятностные комментарии на основе видимого изображения."
        ),
        "uzi_image_upload_label": "Загрузите изображение УЗИ (JPG, PNG)",

        # MRT
        "mrt_subheader": "🧠 МРТ / КТ — анализ изображения",
        "mrt_mode_text": "📝 Заключение рентгенолога (текст)",
        "mrt_mode_image": "🖼️ Загрузить изображение",
        "mrt_scan_type_label": "Тип исследования",
        "mrt_scan_type_opts": [
            "МРТ головного мозга", "МРТ позвоночника", "МРТ сустава",
            "КТ брюшной полости", "КТ грудной клетки",
            "КТ головного мозга", "Другое"
        ],
        "mrt_context_placeholder": "Например: с контрастом, клиническая жалоба, причина направления...",
        "mrt_text_area_label": "Введите текст заключения рентгенолога",
        "mrt_text_placeholder": "Вставьте сюда описание изображения / заключение рентгенолога...",
        "mrt_text_ai_btn": "🤖 Провести клинический анализ заключения с помощью ИИ",
        "mrt_no_text_warning": "⚠️ Сначала введите текст заключения рентгенолога.",
        "mrt_text_spinner": "🧠 ИИ проводит клинический анализ заключения визуализации...",
        "mrt_text_result_header": "🤖 MedLab AI — анализ заключения МРТ/КТ",
        "mrt_text_result_note": (
            "ℹ️ Заключение ИИ основано только на тексте, написанном "
            "рентгенологом. Само изображение не рассматривалось. "
            "Окончательный диагноз и решение о лечении принимает врач."
        ),
        "mrt_image_upload_label": "Загрузите изображение МРТ/КТ (JPG, PNG)",
        "mrt_vision_caption": (
            "⚠️ Внимание: это модель vision-AI, а не рентгенолог. Файлы "
            "DICOM необходимо сначала преобразовать в формат JPG/PNG. "
            "Модель даёт только вероятностные комментарии на основе "
            "видимого изображения."
        ),
        "mrt_image_ai_btn": "🤖 Анализировать изображение с помощью ИИ vision",
        "mrt_no_image_warning": "⚠️ Сначала загрузите файл изображения.",
        "mrt_vision_spinner": "🧠 ИИ анализирует изображение через vision...",
        "mrt_vision_error": (
            "❌ Произошла ошибка при анализе ИИ vision: {err}\n\n"
            "Примечание: название vision-модели Groq может со временем "
            "меняться — проверьте актуальное название модели в консоли "
            "Groq и при необходимости обновите код."
        ),
        "mrt_image_result_header": "🤖 MedLab AI — анализ изображения МРТ/КТ",
        "mrt_image_result_note": (
            "ℹ️ Заключение ИИ vision является предварительным, "
            "вероятностным толкованием на основе загруженного изображения. "
            "Официальное радиологическое заключение и окончательный "
            "диагноз определяет квалифицированный врач."
        ),

        "final_footer": (
            "⚠️ MedLab AI Diagnostics — прототип MVP поддержки клинических "
            "решений. Нормы могут отличаться в зависимости от лаборатории, "
            "возраста, пола и клинического статуса. Окончательное решение "
            "принимает врач."
        ),
    },
}


def t(key, **kwargs):
    """Translate a UI string key into the currently selected language."""
    lang = st.session_state.get("lang", "uz")
    text = TR.get(lang, TR["uz"]).get(key, TR["uz"].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text


def ai_lang_instruction():
    lang = st.session_state.get("lang", "uz")
    return AI_LANG_NAME.get(lang, AI_LANG_NAME["uz"])


# ============================================================
# AI HELPER FUNCTIONS (Groq) — used by all modules
# ============================================================

def get_groq_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])


def ai_text_analysis(prompt):
    """Returns an AI clinical analysis based on text/numeric data: (result, error)."""
    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            model=TEXT_MODEL,
            max_tokens=900,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content, None
    except Exception as e:
        return None, str(e)


def ai_image_analysis(image_file, prompt):
    """Returns an AI vision clinical analysis based on an uploaded image: (result, error).

    Tries each model in VISION_MODELS in order — if one is unavailable or the
    account lacks access to it (404 / model_not_found), it automatically
    falls back to the next model instead of failing outright.
    """
    client = get_groq_client()
    img_bytes = image_file.getvalue()
    b64_image = base64.b64encode(img_bytes).decode("utf-8")
    mime = image_file.type or "image/jpeg"

    last_error = None
    for model_id in VISION_MODELS:
        try:
            response = client.chat.completions.create(
                model=model_id,
                max_tokens=900,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64_image}"}}
                    ]
                }]
            )
            return response.choices[0].message.content, None
        except Exception as e:
            last_error = str(e)
            # If the error indicates the model doesn't exist / no access, try the next one.
            # For any other kind of error (network, rate limit, etc.) also fall through
            # to the next model as a best-effort retry, but keep the last message.
            continue

    return None, last_error


def render_ai_result(session_key, header=None, note=None):
    """Displays the AI result stored in session_state (if present)."""
    if session_key in st.session_state:
        st.subheader(header or t("ai_result_header_default"))
        st.markdown(st.session_state[session_key])
        st.info(note or t("ai_result_note_default"))


def image_upload_ai_section(key_prefix, uploader_label, build_prompt_fn, session_key,
                             button_label=None, note=None):
    """Reusable block: upload an image and analyze it with AI vision."""
    uploaded = st.file_uploader(uploader_label, type=["jpg", "jpeg", "png"], key=f"{key_prefix}_uploader")

    if uploaded is not None:
        st.image(uploaded, caption=t("ai_image_uploaded_caption"), use_container_width=True)

    if st.button(button_label or t("ai_image_btn"), key=f"{key_prefix}_img_ai_btn", use_container_width=True):
        if uploaded is None:
            st.warning(t("ai_no_image_warning"))
        else:
            prompt = build_prompt_fn()
            with st.spinner(t("ai_vision_spinner")):
                result, err = ai_image_analysis(uploaded, prompt)
            if err:
                st.error(t("ai_vision_error", err=err))
            else:
                st.session_state[session_key] = result

    render_ai_result(
        session_key,
        header=t("ai_image_result_header"),
        note=note or t("ai_image_result_note")
    )


# ============================================================
# PAGE CONFIG + LANGUAGE SELECTOR
# ============================================================

st.set_page_config(
    page_title="MedLab AI Diagnostics",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "lang" not in st.session_state:
    st.session_state["lang"] = "uz"

# Language selector — placed at the very top so everything below responds to it
lang_col1, lang_col2, lang_col3 = st.columns([2, 2, 1])
with lang_col3:
    selected_label = st.selectbox(
        t("language_label"),
        options=list(LANGUAGES.values()),
        index=list(LANGUAGES.keys()).index(st.session_state["lang"]),
        key="lang_selector",
        label_visibility="collapsed",
    )
    # Map the selected label back to its language code
    for code, label in LANGUAGES.items():
        if label == selected_label:
            if st.session_state["lang"] != code:
                st.session_state["lang"] = code
                st.rerun()
            break

try:
    logo = Image.open("assets/medlab_logo.png.jpg")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(logo, width=260)
except Exception:
    pass

st.markdown(f"""
<div style="text-align:center; margin-top:-15px;">
    <h1 style="margin-bottom:5px;">MedLab AI Diagnostics</h1>
    <p style="font-size:18px; color:#4CAF50;">
        {t("hero_tagline")}
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================
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

st.markdown(f"""
<div class="hero">
    <h1>{t("app_title")}</h1>
    <p>{t("app_subtitle")}</p>
</div>
""", unsafe_allow_html=True)

st.warning(t("prototype_warning"))

# ============================================================
# PATIENT INFORMATION
# ============================================================

st.header(t("patient_header"))

c1, c2, c3 = st.columns(3)

with c1:
    patient_name = st.text_input(
        t("patient_name"),
        placeholder=t("patient_name_placeholder")
    )

with c2:
    age = st.number_input(
        t("age_label"),
        min_value=0,
        max_value=120,
        value=30,
        step=1
    )

with c3:
    sex_display = st.selectbox(
        t("sex_label"),
        [t("sex_male"), t("sex_female")]
    )
    # Normalize to a language-independent internal value
    sex = "M" if sex_display == t("sex_male") else "F"

complaints = st.text_area(
    t("complaints_label"),
    placeholder=t("complaints_placeholder")
)

st.divider()

# ============================================================
# REFERENCE RANGE
# ============================================================

def get_reference(age, sex):
    # sex: "M" or "F" (language-independent)

    # Adult ranges
    if age >= 18:

        if sex == "M":
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

st.header(t("cbc_input_header"))

col1, col2 = st.columns(2)

with col1:

    st.subheader(t("erythro_subheader"))

    hb = st.number_input(t("hb_label"), min_value=0.0, max_value=30.0, value=13.0, step=0.1)
    rbc = st.number_input(t("rbc_label"), min_value=0.0, max_value=10.0, value=4.5, step=0.1)
    mcv = st.number_input(t("mcv_label"), min_value=0.0, max_value=150.0, value=90.0, step=0.1)
    mch = st.number_input(t("mch_label"), min_value=0.0, max_value=50.0, value=30.0, step=0.1)
    mchc = st.number_input(t("mchc_label"), min_value=0.0, max_value=50.0, value=34.0, step=0.1)
    rdw = st.number_input(t("rdw_label"), min_value=0.0, max_value=40.0, value=13.0, step=0.1)

with col2:

    st.subheader(t("leuko_subheader"))

    wbc = st.number_input(t("wbc_label"), min_value=0.0, max_value=100.0, value=7.0, step=0.1)
    neut = st.number_input(t("neut_label"), min_value=0.0, max_value=100.0, value=55.0, step=0.1)
    lymph = st.number_input(t("lymph_label"), min_value=0.0, max_value=100.0, value=35.0, step=0.1)

    st.subheader(t("plt_subheader"))

    plt = st.number_input(t("plt_label"), min_value=0.0, max_value=1000.0, value=250.0, step=1.0)

# ============================================================
# ANALYSIS FUNCTIONS
# ============================================================

def flag(value, low, high):
    if value < low:
        return "LOW"
    elif value > high:
        return "HIGH"
    return "NORMAL"


def flag_label(status):
    return {"NORMAL": t("status_normal"), "LOW": t("status_low"), "HIGH": t("status_high")}[status]


def flag_icon(status):
    if status == "NORMAL":
        return "🟢"
    if status == "LOW":
        return "🔵"
    return "🔴"


# Indicator display names per language
INDICATOR_NAMES = {
    "uz": {
        "Hb": "Gemoglobin", "RBC": "RBC", "MCV": "MCV", "MCH": "MCH", "MCHC": "MCHC",
        "RDW": "RDW", "WBC": "WBC", "NEU": "Neutrofil", "LYM": "Limfotsit", "PLT": "Trombotsit",
    },
    "en": {
        "Hb": "Hemoglobin", "RBC": "RBC", "MCV": "MCV", "MCH": "MCH", "MCHC": "MCHC",
        "RDW": "RDW", "WBC": "WBC", "NEU": "Neutrophils", "LYM": "Lymphocytes", "PLT": "Platelets",
    },
    "ru": {
        "Hb": "Гемоглобин", "RBC": "RBC", "MCV": "MCV", "MCH": "MCH", "MCHC": "MCHC",
        "RDW": "RDW", "WBC": "WBC", "NEU": "Нейтрофилы", "LYM": "Лимфоциты", "PLT": "Тромбоциты",
    },
}


def iname(key):
    lang = st.session_state.get("lang", "uz")
    return INDICATOR_NAMES.get(lang, INDICATOR_NAMES["uz"])[key]


results = {
    "Hb": {"value": hb, "unit": "g/dL", "range": ref["Hb"], "status": flag(hb, *ref["Hb"])},
    "RBC": {"value": rbc, "unit": "×10¹²/L", "range": ref["RBC"], "status": flag(rbc, *ref["RBC"])},
    "MCV": {"value": mcv, "unit": "fL", "range": ref["MCV"], "status": flag(mcv, *ref["MCV"])},
    "MCH": {"value": mch, "unit": "pg", "range": ref["MCH"], "status": flag(mch, *ref["MCH"])},
    "MCHC": {"value": mchc, "unit": "g/dL", "range": ref["MCHC"], "status": flag(mchc, *ref["MCHC"])},
    "RDW": {"value": rdw, "unit": "%", "range": ref["RDW"], "status": flag(rdw, *ref["RDW"])},
    "WBC": {"value": wbc, "unit": "×10⁹/L", "range": ref["WBC"], "status": flag(wbc, *ref["WBC"])},
    "NEU": {"value": neut, "unit": "%", "range": ref["NEU"], "status": flag(neut, *ref["NEU"])},
    "LYM": {"value": lymph, "unit": "%", "range": ref["LYM"], "status": flag(lymph, *ref["LYM"])},
    "PLT": {"value": plt, "unit": "×10⁹/L", "range": ref["PLT"], "status": flag(plt, *ref["PLT"])},
}

# ============================================================
# ANALYZE BUTTON
# ============================================================

st.divider()

analyze = st.button(t("analyze_button"), use_container_width=True, type="primary")

if analyze:

    # --------------------------------------------------------
    # TABLE
    # --------------------------------------------------------

    st.header(t("results_header"))

    rows = []

    for key, item in results.items():
        low, high = item["range"]
        rows.append({
            t("col_indicator"): iname(key),
            t("col_result"): item["value"],
            t("col_unit"): item["unit"],
            t("col_reference"): f"{low} – {high}",
            t("col_status"): f"{flag_icon(item['status'])} {flag_label(item['status'])}"
        })

    df = pd.DataFrame(rows)

    st.dataframe(df, use_container_width=True, hide_index=True)

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    abnormal = [key for key, item in results.items() if item["status"] != "NORMAL"]

    st.header(t("interpretation_header"))

    if len(abnormal) == 0:

        st.markdown(f"""
        <div class="normal-box">
        <h3>{t("no_abnormal_title")}</h3>
        {t("no_abnormal_text")}
        </div>
        """, unsafe_allow_html=True)

    else:

        st.markdown(
            f"""
            <div class="warning-box">
            <h3>{t("abnormal_title", count=len(abnormal))}</h3>
            {t("abnormal_text")}
            </div>
            """,
            unsafe_allow_html=True
        )

        for key in abnormal:

            item = results[key]
            low, high = item["range"]
            name = iname(key)

            if item["status"] == "LOW":
                st.write(t("low_line", name=name, value=item["value"], unit=item["unit"], low=low, high=high))
            else:
                st.write(t("high_line", name=name, value=item["value"], unit=item["unit"], low=low, high=high))

    # --------------------------------------------------------
    # CLINICAL PATTERN DETECTION
    # --------------------------------------------------------

    st.subheader(t("pattern_header"))

    # Clinical finding/recommendation templates per language
    FMSG = {
        "uz": {
            "anemia_flag": "Gemoglobin kamaygan — anemiya mavjudligini klinik jihatdan baholash kerak.",
            "microcytic": "Hb pasayishi + MCV pastligi mikrotsitar anemiya yo‘nalishini ko‘rsatishi mumkin.",
            "microcytic_rec": "Temir almashinuvi: ferritin, transferrin saturation va zarurat bo‘lsa CRP ko‘rib chiqilsin.",
            "macrocytic": "Hb pasayishi + MCV yuqoriligi makrotsitar anemiya yo‘nalishini ko‘rsatishi mumkin.",
            "macrocytic_rec": "Vitamin B12 va folat holatini klinik vaziyatga qarab baholash.",
            "normocytic": "Normotsitar anemiya ehtimoli mavjud.",
            "normocytic_rec": "Qon yo‘qotilishi, surunkali kasalliklar va boshqa sabablar klinik jihatdan baholansin.",
            "leukocytosis": "Leykotsitlar soni yuqori — leykotsitoz.",
            "leukocytosis_rec": "Infeksiya, yallig‘lanish, stress va dori ta’siri klinik belgilar bilan birga baholansin.",
            "leukopenia": "Leykotsitlar soni past — leykopeniya.",
            "leukopenia_rec": "Virusli infeksiyalar, dori ta’siri va boshqa sabablarni klinik vaziyatga qarab baholash.",
            "neutrophilia": "Neytrofillar ulushi yuqori — neytrofil yo‘nalishdagi o‘zgarish.",
            "neutropenia": "Neytrofillar ulushi past — neytropeniya ehtimoli.",
            "lymphocytosis": "Limfotsitlar ulushi yuqori — limfotsitoz.",
            "thrombocytopenia": "Trombotsitlar soni past — trombotsitopeniya.",
            "thrombocytopenia_rec": "Qon ketish belgilari bo‘lsa shoshilinch klinik baholash zarur; natijani qayta tekshirish va sababini aniqlash ko‘rib chiqilsin.",
            "thrombocytosis": "Trombotsitlar soni yuqori — trombotsitoz.",
            "thrombocytosis_rec": "Reaktiv sabablar, yallig‘lanish va temir tanqisligi klinik vaziyatga qarab baholansin.",
        },
        "en": {
            "anemia_flag": "Hemoglobin is decreased — the presence of anemia should be evaluated clinically.",
            "microcytic": "Decreased Hb + low MCV may suggest a microcytic anemia pattern.",
            "microcytic_rec": "Consider iron studies: ferritin, transferrin saturation, and CRP if needed.",
            "macrocytic": "Decreased Hb + high MCV may suggest a macrocytic anemia pattern.",
            "macrocytic_rec": "Evaluate vitamin B12 and folate status depending on the clinical situation.",
            "normocytic": "Possible normocytic anemia.",
            "normocytic_rec": "Blood loss, chronic disease, and other causes should be evaluated clinically.",
            "leukocytosis": "White blood cell count is elevated — leukocytosis.",
            "leukocytosis_rec": "Infection, inflammation, stress, and medication effects should be evaluated together with clinical signs.",
            "leukopenia": "White blood cell count is low — leukopenia.",
            "leukopenia_rec": "Evaluate viral infections, medication effects, and other causes based on the clinical situation.",
            "neutrophilia": "Neutrophil proportion is elevated — a neutrophilic shift.",
            "neutropenia": "Neutrophil proportion is low — possible neutropenia.",
            "lymphocytosis": "Lymphocyte proportion is elevated — lymphocytosis.",
            "thrombocytopenia": "Platelet count is low — thrombocytopenia.",
            "thrombocytopenia_rec": "If there are bleeding signs, urgent clinical evaluation is needed; consider retesting and determining the cause.",
            "thrombocytosis": "Platelet count is elevated — thrombocytosis.",
            "thrombocytosis_rec": "Reactive causes, inflammation, and iron deficiency should be evaluated depending on the clinical situation.",
        },
        "ru": {
            "anemia_flag": "Гемоглобин снижен — наличие анемии следует оценить клинически.",
            "microcytic": "Снижение Hb + низкий MCV может указывать на микроцитарную анемию.",
            "microcytic_rec": "Рассмотреть обмен железа: ферритин, насыщение трансферрина, при необходимости СРБ.",
            "macrocytic": "Снижение Hb + высокий MCV может указывать на макроцитарную анемию.",
            "macrocytic_rec": "Оценить уровень витамина B12 и фолиевой кислоты в зависимости от клинической ситуации.",
            "normocytic": "Возможна нормоцитарная анемия.",
            "normocytic_rec": "Следует клинически оценить кровопотерю, хронические заболевания и другие причины.",
            "leukocytosis": "Количество лейкоцитов повышено — лейкоцитоз.",
            "leukocytosis_rec": "Инфекцию, воспаление, стресс и действие препаратов следует оценивать вместе с клиническими признаками.",
            "leukopenia": "Количество лейкоцитов снижено — лейкопения.",
            "leukopenia_rec": "Оценить вирусные инфекции, действие препаратов и другие причины в зависимости от клинической ситуации.",
            "neutrophilia": "Доля нейтрофилов повышена — нейтрофильный сдвиг.",
            "neutropenia": "Доля нейтрофилов снижена — возможна нейтропения.",
            "lymphocytosis": "Доля лимфоцитов повышена — лимфоцитоз.",
            "thrombocytopenia": "Количество тромбоцитов снижено — тромбоцитопения.",
            "thrombocytopenia_rec": "При наличии признаков кровотечения требуется срочная клиническая оценка; рассмотреть повторное исследование и выяснение причины.",
            "thrombocytosis": "Количество тромбоцитов повышено — тромбоцитоз.",
            "thrombocytosis_rec": "Реактивные причины, воспаление и дефицит железа следует оценивать в зависимости от клинической ситуации.",
        },
    }

    def fm(key):
        lang = st.session_state.get("lang", "uz")
        return FMSG.get(lang, FMSG["uz"])[key]

    findings = []
    recommendations = []

    # Anemia pattern
    if hb < ref["Hb"][0]:

        findings.append(fm("anemia_flag"))

        if mcv < ref["MCV"][0]:
            findings.append(fm("microcytic"))
            recommendations.append(fm("microcytic_rec"))
        elif mcv > ref["MCV"][1]:
            findings.append(fm("macrocytic"))
            recommendations.append(fm("macrocytic_rec"))
        else:
            findings.append(fm("normocytic"))
            recommendations.append(fm("normocytic_rec"))

    # Leukocytosis
    if wbc > ref["WBC"][1]:
        findings.append(fm("leukocytosis"))
        recommendations.append(fm("leukocytosis_rec"))

    # Leukopenia
    if wbc < ref["WBC"][0]:
        findings.append(fm("leukopenia"))
        recommendations.append(fm("leukopenia_rec"))

    # Neutrophilia
    if neut > ref["NEU"][1]:
        findings.append(fm("neutrophilia"))

    # Neutropenia
    if neut < ref["NEU"][0]:
        findings.append(fm("neutropenia"))

    # Lymphocytosis
    if lymph > ref["LYM"][1]:
        findings.append(fm("lymphocytosis"))

    # Thrombocytopenia
    if plt < ref["PLT"][0]:
        findings.append(fm("thrombocytopenia"))
        recommendations.append(fm("thrombocytopenia_rec"))

    # Thrombocytosis
    if plt > ref["PLT"][1]:
        findings.append(fm("thrombocytosis"))
        recommendations.append(fm("thrombocytosis_rec"))

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    if not findings:
        st.success(t("no_pattern"))
    else:
        for finding in findings:
            st.write("• " + finding)

    # --------------------------------------------------------
    # RECOMMENDATIONS
    # --------------------------------------------------------

    st.subheader(t("recommendations_header"))

    if recommendations:
        for recommendation in recommendations:
            st.write("• " + recommendation)
    else:
        st.write("• " + t("recommendations_default"))

    # --------------------------------------------------------
    # OVERALL STATUS
    # --------------------------------------------------------

    st.header(t("overall_header"))

    severe = False

    if plt < 50:
        severe = True

    if hb < 8:
        severe = True

    if wbc < 2 or wbc > 30:
        severe = True

    if severe:

        st.markdown(f"""
        <div class="danger-box">
        <h3>{t("overall_severe_title")}</h3>
        {t("overall_severe_text")}
        </div>
        """, unsafe_allow_html=True)

    elif abnormal:
        st.warning(t("overall_abnormal"))
    else:
        st.success(t("overall_normal"))

    # --------------------------------------------------------
    # AI DEEP ANALYSIS (CBC)
    # --------------------------------------------------------

    st.divider()
    st.header(t("ai_extra_header"))

    if st.button(t("ai_cbc_btn"), key="cbc_ai_btn", use_container_width=True):

        cbc_context = "\n".join(
            f"{iname(key)}: {item['value']} {item['unit']} "
            f"(reference: {item['range'][0]}-{item['range'][1]}) — {flag_label(item['status'])}"
            for key, item in results.items()
        )

        cbc_prompt = f"""
You are the MedLab AI Diagnostics clinical decision support system.

Patient: {age} years old, {sex_display}
Complaints: {complaints or t("not_specified")}

CBC results:
{cbc_context}

System-detected findings:
{chr(10).join(findings) if findings else "No significant pattern detected."}

Carefully analyze these CBC results from a clinical perspective, in more depth.

Respond in {ai_lang_instruction()}, structured as follows:

1. 📊 Overall assessment
2. 🔎 Significant laboratory changes
3. 🧩 Possible clinical directions
4. 💡 Recommended next investigations
5. 👨‍⚕️ Brief summary for the physician

Important:
- Do not firmly confirm a diagnosis.
- Only indicate possible directions based on the laboratory results.
- The final clinical decision is made by the physician.
"""

        with st.spinner(t("ai_spinner_cbc")):
            cbc_ai_result, cbc_ai_err = ai_text_analysis(cbc_prompt)

        if cbc_ai_err:
            st.error(t("ai_error", err=cbc_ai_err))
        else:
            st.session_state["ai_cbc_result"] = cbc_ai_result

    render_ai_result("ai_cbc_result", header=t("ai_cbc_result_header"))

    st.markdown(t("ai_image_or"))

    image_upload_ai_section(
        key_prefix="cbc",
        uploader_label=t("ai_image_upload_label"),
        build_prompt_fn=lambda: f"""
You are the MedLab AI Diagnostics clinical decision support system.

Patient: {age} years old, {sex_display}
Complaints: {complaints or t("not_specified")}

The attached image contains a CBC (complete blood count) result form.
Read the visible indicators in the image and comment on them carefully from a clinical perspective.

Respond in {ai_lang_instruction()}, structured as follows:

1. 📊 Main indicators read from the image
2. 🔎 Notable deviations
3. 🧩 Possible clinical directions
4. 💡 Recommended next investigations
5. 👨‍⚕️ Brief summary for the physician

IMPORTANT: Clearly note that image quality may be low or text unclear.
Do not firmly confirm a diagnosis.
""",
        session_key="ai_cbc_image_result"
    )

    # --------------------------------------------------------
    # PDF REPORT
    # --------------------------------------------------------

    st.divider()
    st.header(t("report_header"))

    report_text = f"""
{t("report_title")}
{t("report_subtitle")}

{t("report_date")}: {datetime.now().strftime("%Y-%m-%d %H:%M")}

{t("report_patient")}: {patient_name or t("not_specified")}
{t("report_age")}: {age}
{t("report_sex")}: {sex_display}

{t("report_clinical_info")}:
{complaints or t("not_specified")}

{t("report_cbc_results")}
----------------------------------------
"""

    for key, item in results.items():
        low, high = item["range"]
        report_text += (
            f"{iname(key)}: {item['value']} {item['unit']} | "
            f"{t('col_reference')}: {low}-{high} | {flag_label(item['status'])}\n"
        )

    report_text += f"\n{t('report_interpretation')}\n----------------------------------------\n"

    if findings:
        for finding in findings:
            report_text += "- " + finding + "\n"
    else:
        report_text += "- " + t("report_no_pattern") + "\n"

    report_text += f"\n{t('report_recommendations')}\n----------------------------------------\n"

    for recommendation in recommendations:
        report_text += "- " + recommendation + "\n"

    report_text += "\n\n" + t("report_footer") + "\n"

    pdf_bytes = None

    try:

        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas

        buffer = BytesIO()

        pdf = canvas.Canvas(buffer, pagesize=A4)

        width, height = A4
        y = height - 50

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(40, y, "MedLab AI Diagnostics Hub")

        y -= 30

        pdf.setFont("Helvetica", 9)

        for line in report_text.split("\n"):

            if y < 40:
                pdf.showPage()
                y = height - 50
                pdf.setFont("Helvetica", 9)

            pdf.drawString(40, y, line[:115])

            y -= 13

        pdf.save()

        pdf_bytes = buffer.getvalue()

    except Exception:
        pdf_bytes = None

    if pdf_bytes:

        st.download_button(
            t("download_pdf"),
            data=pdf_bytes,
            file_name="MedLab_CBC_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    else:

        st.download_button(
            t("download_txt"),
            data=report_text,
            file_name="MedLab_CBC_Report.txt",
            mime="text/plain",
            use_container_width=True
        )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(t("footer_caption"))
st.caption(t("footer_caption2"))

# ============================================================
# ADDITIONAL MODULES: URINALYSIS AND BIOCHEMISTRY
# ============================================================

st.divider()
st.header(t("extra_modules_header"))

analysis_type = st.selectbox(
    t("analysis_type_label"),
    [
        t("analysis_cbc"),
        t("analysis_uat"),
        t("analysis_bio"),
        t("analysis_uzi"),
        t("analysis_mrt"),
    ]
)

if analysis_type == t("analysis_uat"):

    st.subheader(t("uat_subheader"))

    col1, col2 = st.columns(2)

    with col1:
        urine_color = st.selectbox(t("uat_color"), t("uat_color_opts"))
        urine_clarity = st.selectbox(t("uat_clarity"), t("uat_clarity_opts"))
        urine_ph = st.number_input(t("uat_ph"), min_value=3.0, max_value=10.0, value=6.0)
        urine_density = st.number_input(t("uat_density"), min_value=1.000, max_value=1.050, value=1.020, format="%.3f")

    with col2:
        protein = st.selectbox(t("uat_protein"), t("uat_protein_opts"))
        glucose = st.selectbox(t("uat_glucose"), t("uat_glucose_opts"))
        blood = st.selectbox(t("uat_blood"), t("uat_blood_opts"))
        leukocytes = st.number_input(t("uat_leukocytes"), min_value=0, max_value=100, value=2)

    if st.button(t("uat_analyze_btn")):

        # Language-independent checks use option index (0 = negative/first option)
        protein_opts = t("uat_protein_opts")
        glucose_opts = t("uat_glucose_opts")
        blood_opts = t("uat_blood_opts")

        urine_findings = []
        urine_recommendations = []

        UMSG = {
            "uz": {
                "ph": "pH me'yoriy diapazondan tashqarida.",
                "ph_rec": "Klinik holat va ovqatlanish bilan birgalikda baholash.",
                "density": "Nisbiy zichlik o'zgargan.",
                "density_rec": "Suyuqlik balansi va buyrak faoliyatini baholash.",
                "protein": "Siydikda oqsil aniqlangan.",
                "protein_rec": "Proteinuriyani qayta tekshirish va klinik baholash.",
                "glucose": "Siydikda glyukoza aniqlangan.",
                "glucose_rec": "Qon glyukozasi va diabet bo'yicha baholash.",
                "blood": "Siydikda qon/eritrotsit belgisi mavjud.",
                "blood_rec": "Siydik cho'kmasi va klinik simptomlarni baholash.",
                "leuko": "Leykotsitlar ko'paygan.",
                "leuko_rec": "Siydik yo'llari yallig'lanishi/infeksiyasi ehtimolini baholash.",
            },
            "en": {
                "ph": "pH is outside the normal range.",
                "ph_rec": "Evaluate together with the clinical status and diet.",
                "density": "Specific gravity is altered.",
                "density_rec": "Evaluate fluid balance and kidney function.",
                "protein": "Protein detected in urine.",
                "protein_rec": "Retest for proteinuria and evaluate clinically.",
                "glucose": "Glucose detected in urine.",
                "glucose_rec": "Evaluate blood glucose and diabetes status.",
                "blood": "Blood/erythrocyte marker present in urine.",
                "blood_rec": "Evaluate urine sediment and clinical symptoms.",
                "leuko": "Leukocytes are increased.",
                "leuko_rec": "Evaluate for possible urinary tract inflammation/infection.",
            },
            "ru": {
                "ph": "pH выходит за пределы нормы.",
                "ph_rec": "Оценивать совместно с клиническим состоянием и питанием.",
                "density": "Относительная плотность изменена.",
                "density_rec": "Оценить водный баланс и функцию почек.",
                "protein": "В моче обнаружен белок.",
                "protein_rec": "Повторно проверить протеинурию и провести клиническую оценку.",
                "glucose": "В моче обнаружена глюкоза.",
                "glucose_rec": "Оценить уровень глюкозы крови и статус по диабету.",
                "blood": "В моче обнаружены признаки крови/эритроцитов.",
                "blood_rec": "Оценить осадок мочи и клинические симптомы.",
                "leuko": "Лейкоциты повышены.",
                "leuko_rec": "Оценить вероятность воспаления/инфекции мочевыводящих путей.",
            },
        }

        def um(key):
            lang = st.session_state.get("lang", "uz")
            return UMSG.get(lang, UMSG["uz"])[key]

        if urine_ph < 5.0 or urine_ph > 8.0:
            urine_findings.append(um("ph"))
            urine_recommendations.append(um("ph_rec"))

        if urine_density < 1.005 or urine_density > 1.030:
            urine_findings.append(um("density"))
            urine_recommendations.append(um("density_rec"))

        if protein != protein_opts[0]:
            urine_findings.append(um("protein"))
            urine_recommendations.append(um("protein_rec"))

        if glucose == glucose_opts[1]:
            urine_findings.append(um("glucose"))
            urine_recommendations.append(um("glucose_rec"))

        if blood != blood_opts[0]:
            urine_findings.append(um("blood"))
            urine_recommendations.append(um("blood_rec"))

        if leukocytes > 5:
            urine_findings.append(um("leuko"))
            urine_recommendations.append(um("leuko_rec"))

        # Save to session_state so results persist when the AI button reruns the page
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

    if "urine_findings" in st.session_state:

        urine_findings = st.session_state["urine_findings"]
        urine_recommendations = st.session_state["urine_recommendations"]
        saved_inputs = st.session_state["urine_inputs"]

        st.subheader(t("uat_result_header"))

        if not urine_findings:
            st.success(t("uat_no_findings"))
        else:
            st.warning(t("uat_has_findings"))

            for finding in urine_findings:
                st.write("•", finding)

            st.subheader(t("recommendations_header"))

            for recommendation in urine_recommendations:
                st.write("•", recommendation)

        if st.button(t("uat_ai_btn"), key="uat_ai_btn"):

            try:
                client = get_groq_client()

                urine_context = f"""
Patient's urinalysis (UAT) results:

pH: {saved_inputs['ph']}
Specific gravity: {saved_inputs['density']}
Protein: {saved_inputs['protein']}
Glucose: {saved_inputs['glucose']}
Blood/erythrocytes: {saved_inputs['blood']}
Leukocytes: {saved_inputs['leukocytes']} per field of view

System-detected deviations:
{chr(10).join(urine_findings) if urine_findings else "No significant deviation detected."}
"""

                with st.spinner(t("uat_ai_spinner")):

                    response = client.chat.completions.create(
                        model=TEXT_MODEL,
                        max_tokens=900,
                        messages=[
                            {
                                "role": "user",
                                "content": f"""
You are the MedLab AI Diagnostics clinical decision support system.

Carefully interpret the following urinalysis results from a clinical perspective.

{urine_context}

Respond in {ai_lang_instruction()}, structured as follows:

1. 📊 Overall assessment
2. 🔎 Significant laboratory changes
3. 🧩 Possible clinical directions
4. 💡 Recommended next investigations
5. 👨‍⚕️ Brief summary for the physician

Important:
- Do not firmly confirm a diagnosis.
- Only indicate possible directions based on the laboratory results.
- Note that the patient's age, sex, symptoms, and laboratory reference ranges should be taken into account.
- The final clinical decision is made by the physician.
"""
                            }
                        ]
                    )

                st.session_state["ai_urine_result"] = response.choices[0].message.content

            except Exception as e:
                st.error(t("ai_error", err=e))

        if "ai_urine_result" in st.session_state:

            st.subheader(t("uat_ai_result_header"))
            st.markdown(st.session_state["ai_urine_result"])
            st.info(t("ai_result_note_default"))

    st.divider()
    st.markdown(t("uat_image_or"))

    image_upload_ai_section(
        key_prefix="uat",
        uploader_label=t("uat_image_upload_label"),
        build_prompt_fn=lambda: f"""
You are the MedLab AI Diagnostics clinical decision support system.

Patient: {age} years old, {sex_display}
Complaints: {complaints or t("not_specified")}

The attached image contains a urinalysis (UAT) result form.
Read the visible indicators in the image and comment on them carefully from a clinical perspective.

Respond in {ai_lang_instruction()}, structured as follows:

1. 📊 Main indicators read from the image
2. 🔎 Notable deviations
3. 🧩 Possible clinical directions
4. 💡 Recommended next investigations
5. 👨‍⚕️ Brief summary for the physician

IMPORTANT: Clearly note that image quality may be low or text unclear.
Do not firmly confirm a diagnosis.
""",
        session_key="ai_uat_image_result"
    )

elif analysis_type == t("analysis_bio"):

    st.subheader(t("bio_subheader"))

    col1, col2 = st.columns(2)

    with col1:
        glucose_bio = st.number_input(t("bio_glucose"), min_value=0.0, value=5.0)
        creatinine = st.number_input(t("bio_creatinine"), min_value=0.0, value=80.0)
        urea = st.number_input(t("bio_urea"), min_value=0.0, value=5.0)
        alt = st.number_input(t("bio_alt"), min_value=0.0, value=25.0)

    with col2:
        ast = st.number_input(t("bio_ast"), min_value=0.0, value=25.0)
        bilirubin = st.number_input(t("bio_bilirubin"), min_value=0.0, value=12.0)
        total_protein = st.number_input(t("bio_protein"), min_value=0.0, value=70.0)
        cholesterol = st.number_input(t("bio_cholesterol"), min_value=0.0, value=4.5)

    if st.button(t("bio_ai_btn"), key="bio_ai_btn"):

        try:
            client = get_groq_client()

            patient_context = f"""
            Patient's blood biochemistry results:

            Glucose: {glucose_bio} mmol/L
            Creatinine: {creatinine} µmol/L
            Urea: {urea} mmol/L
            ALT: {alt} U/L
            AST: {ast} U/L
            Total bilirubin: {bilirubin} µmol/L
            Total protein: {total_protein} g/L
            Total cholesterol: {cholesterol} mmol/L
            """

            with st.spinner(t("bio_ai_spinner")):

                response = client.chat.completions.create(
                    model=TEXT_MODEL,
                    max_tokens=900,
                    messages=[
                        {
                            "role": "user",
                            "content": f"""
                    You are the MedLab AI Diagnostics clinical decision support system.

                    Carefully analyze the following blood biochemistry results from a clinical perspective.

                    {patient_context}

                    Respond in {ai_lang_instruction()}.

                    Structure your response as follows:

                    1. 📊 Overall assessment
                    2. 🔎 Significant deviations
                    3. 🧩 Possible clinical directions
                    4. 🧪 Recommended additional investigations
                    5. 👨‍⚕️ Brief summary for the physician

                    Evaluate each result together, not in isolation.
                    Do not make a final diagnosis based on a single laboratory indicator.

                    Normal ranges may vary depending on the laboratory method, the
                    patient's age, sex, and clinical status.

                    Do not firmly confirm a diagnosis and do not prescribe medication
                    in place of the physician.
                    """
                        }
                    ]
                )

            st.session_state["ai_bio_result"] = response.choices[0].message.content

        except Exception as e:
            st.error(t("ai_error", err=e))

    if "ai_bio_result" in st.session_state:

        st.subheader(t("bio_ai_result_header"))
        st.markdown(st.session_state["ai_bio_result"])
        st.info(t("ai_result_note_default"))

    st.divider()
    st.markdown(t("bio_image_or"))

    image_upload_ai_section(
        key_prefix="bio",
        uploader_label=t("bio_image_upload_label"),
        build_prompt_fn=lambda: f"""
You are the MedLab AI Diagnostics clinical decision support system.

Patient: {age} years old, {sex_display}
Complaints: {complaints or t("not_specified")}

The attached image contains a blood biochemistry result form.
Read the visible indicators in the image and comment on them carefully from a clinical perspective.

Respond in {ai_lang_instruction()}, structured as follows:

1. 📊 Main indicators read from the image
2. 🔎 Notable deviations
3. 🧩 Possible clinical directions
4. 💡 Recommended next investigations
5. 👨‍⚕️ Brief summary for the physician

IMPORTANT: Clearly note that image quality may be low or text unclear.
Do not firmly confirm a diagnosis.
""",
        session_key="ai_bio_image_result"
    )

elif analysis_type == t("analysis_uzi"):

    st.subheader(t("uzi_subheader"))

    uzi_mode = st.radio(
        t("input_mode_label"),
        [t("mode_text"), t("mode_image")],
        horizontal=True,
        key="uzi_mode"
    )

    uzi_area = st.selectbox(t("uzi_area_label"), t("uzi_area_opts"), key="uzi_area")

    uzi_note = st.text_input(
        t("extra_context_label"),
        placeholder=t("extra_context_placeholder"),
        key="uzi_note"
    )

    if uzi_mode == t("mode_text"):

        uzi_text_input = st.text_area(
            t("uzi_text_area_label"),
            height=200,
            placeholder=t("uzi_text_placeholder"),
            key="uzi_text_input"
        )

        if st.button(t("uzi_text_ai_btn"), key="uzi_text_ai_btn"):

            if not uzi_text_input.strip():
                st.warning(t("uzi_no_text_warning"))
            else:
                uzi_prompt = f"""
You are the MedLab AI Diagnostics clinical decision support system.

Examination area: {uzi_area}
Additional context: {uzi_note or t("not_specified")}
Patient: {age} years old, {sex_display}
Complaints: {complaints or t("not_specified")}

Ultrasound report text written by the physician:
\"\"\"{uzi_text_input}\"\"\"

Carefully comment on this ultrasound report from a clinical perspective.

Respond in {ai_lang_instruction()}, structured as follows:

1. 📊 Overall assessment
2. 🔎 Main findings in the report
3. 🧩 Possible clinical directions
4. 💡 Recommended follow-up investigations/consultations
5. 👨‍⚕️ Brief summary for the physician

Important:
- You have not seen the image itself, only the written report — mention this in your response.
- Do not firmly confirm a final diagnosis.
- The final clinical decision is made by the physician.
"""
                with st.spinner(t("uzi_text_spinner")):
                    uzi_text_result, uzi_text_err = ai_text_analysis(uzi_prompt)

                if uzi_text_err:
                    st.error(t("ai_error", err=uzi_text_err))
                else:
                    st.session_state["ai_uzi_text_result"] = uzi_text_result

        render_ai_result(
            "ai_uzi_text_result",
            header=t("uzi_text_result_header"),
            note=t("uzi_text_result_note")
        )

    else:

        st.caption(t("uzi_vision_caption"))

        image_upload_ai_section(
            key_prefix="uzi",
            uploader_label=t("uzi_image_upload_label"),
            build_prompt_fn=lambda: f"""
You are the MedLab AI Diagnostics clinical decision support system.

Examination area: {uzi_area}
Additional context: {uzi_note or t("not_specified")}
Patient: {age} years old, {sex_display}
Complaints: {complaints or t("not_specified")}

Review the attached ultrasound image and describe it carefully from a clinical perspective.

Respond in {ai_lang_instruction()}, structured as follows:

1. 📊 Overall picture visible in the image
2. 🔎 Notable findings (if any)
3. 🧩 Possible clinical directions
4. 💡 Recommended follow-up investigations/consultations
5. 👨‍⚕️ Brief summary for the physician

IMPORTANT LIMITATIONS:
- You are not a sonographer/radiologist, only an AI vision assistant.
- Clearly note that image quality may be low.
- Never firmly confirm a final diagnosis.
- Always emphasize the need for a formal examination by a qualified specialist.
""",
            session_key="ai_uzi_image_result",
            note=t("ai_image_result_note")
        )

elif analysis_type == t("analysis_mrt"):

    st.subheader(t("mrt_subheader"))

    input_mode = st.radio(
        t("input_mode_label"),
        [t("mrt_mode_text"), t("mrt_mode_image")],
        horizontal=True
    )

    scan_type = st.selectbox(t("mrt_scan_type_label"), t("mrt_scan_type_opts"))

    scan_area_note = st.text_input(
        t("extra_context_label"),
        placeholder=t("mrt_context_placeholder")
    )

    # ----------------------------------------------------
    # TEXT MODE — enter radiologist's report as text
    # ----------------------------------------------------
    if input_mode == t("mrt_mode_text"):

        report_text_input = st.text_area(
            t("mrt_text_area_label"),
            height=200,
            placeholder=t("mrt_text_placeholder")
        )

        if st.button(t("mrt_text_ai_btn"), key="mrt_text_ai_btn"):

            if not report_text_input.strip():
                st.warning(t("mrt_no_text_warning"))
            else:
                try:
                    client = get_groq_client()

                    with st.spinner(t("mrt_text_spinner")):

                        response = client.chat.completions.create(
                            model=TEXT_MODEL,
                            max_tokens=900,
                            messages=[
                                {
                                    "role": "user",
                                    "content": f"""
You are the MedLab AI Diagnostics clinical decision support system.

Examination type: {scan_type}
Additional context: {scan_area_note or t("not_specified")}
Patient: {age} years old, {sex_display}
Complaints: {complaints or t("not_specified")}

Report text written by the radiologist:
\"\"\"{report_text_input}\"\"\"

Carefully comment on this radiology report from a clinical perspective.

Respond in {ai_lang_instruction()}, structured as follows:

1. 📊 Overall assessment
2. 🔎 Main findings in the report
3. 🧩 Possible clinical directions
4. 💡 Recommended follow-up investigations/consultations
5. 👨‍⚕️ Brief summary for the physician

Important:
- You have not seen the image itself, only the written report — mention this in your response.
- Do not firmly confirm a final diagnosis.
- The final clinical decision is made by the physician.
"""
                                }
                            ]
                        )

                    st.session_state["ai_mrt_text_result"] = response.choices[0].message.content

                except Exception as e:
                    st.error(t("ai_error", err=e))

        if "ai_mrt_text_result" in st.session_state:

            st.subheader(t("mrt_text_result_header"))
            st.markdown(st.session_state["ai_mrt_text_result"])
            st.info(t("mrt_text_result_note"))

    # ----------------------------------------------------
    # IMAGE MODE — send image to the vision model
    # ----------------------------------------------------
    else:

        uploaded_scan = st.file_uploader(
            t("mrt_image_upload_label"),
            type=["jpg", "jpeg", "png"]
        )

        st.caption(t("mrt_vision_caption"))

        if uploaded_scan is not None:
            st.image(uploaded_scan, caption=t("ai_image_uploaded_caption"), use_container_width=True)

        if st.button(t("mrt_image_ai_btn"), key="mrt_image_ai_btn"):

            if uploaded_scan is None:
                st.warning(t("mrt_no_image_warning"))
            else:
                prompt_text = f"""
You are the MedLab AI Diagnostics clinical decision support system.

Examination type: {scan_type}
Additional context: {scan_area_note or t("not_specified")}
Patient: {age} years old, {sex_display}
Complaints: {complaints or t("not_specified")}

Review the attached MRI/CT image and describe it carefully from a clinical perspective.

Respond in {ai_lang_instruction()}, structured as follows:

1. 📊 Overall picture visible in the image
2. 🔎 Notable findings (if any)
3. 🧩 Possible clinical directions
4. 💡 Recommended follow-up investigations/consultations
5. 👨‍⚕️ Brief summary for the physician

IMPORTANT LIMITATIONS:
- You are not a radiologist, only an AI vision assistant.
- Clearly note the possibility of error due to image quality, projection, and lack of contrast.
- Never firmly confirm a final diagnosis.
- Always emphasize the need for a formal examination by a qualified radiologist/physician.
"""

                with st.spinner(t("mrt_vision_spinner")):
                    mrt_image_result, mrt_image_err = ai_image_analysis(uploaded_scan, prompt_text)

                if mrt_image_err:
                    st.error(t("mrt_vision_error", err=mrt_image_err))
                else:
                    st.session_state["ai_mrt_image_result"] = mrt_image_result

        if "ai_mrt_image_result" in st.session_state:

            st.subheader(t("mrt_image_result_header"))
            st.markdown(st.session_state["ai_mrt_image_result"])
            st.info(t("mrt_image_result_note"))

st.caption(t("final_footer"))
