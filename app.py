import json
import streamlit as st
from pathlib import Path
import pandas as pd
import streamlit.components.v1 as components

# -------------------------------------------------------
# Настройки страницы
# -------------------------------------------------------

st.set_page_config(
    page_title="Генератор комментариев",
    page_icon="📄",
    layout="wide"
)


# -------------------------------------------------------
# Загрузка данных
# -------------------------------------------------------

BASE_DIR = Path(__file__).parent


def load_subjects():

    with open(
        BASE_DIR / "subjects.json",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def load_templates():

    with open(
        BASE_DIR / "templates.json",
        encoding="utf-8"
    ) as f:

        return json.load(f)["templates"]


subjects = load_subjects()

templates = load_templates()

with open("scores.json", "r", encoding="utf-8") as f:
    scores = json.load(f)

table = []

for subject, values in scores.items():
    table.append({
        "Предмет": subject,
        "Бюджет": values["Бюджет"],
        "Договор": values["Договор"]
    })

df_scores = pd.DataFrame(table)

# -------------------------------------------------------
# Служебные функции
# -------------------------------------------------------

def format_subjects(selected):

    if len(selected) == 1:

        return f'по предмету «{selected[0]}»'

    return "по предметам " + ", ".join(
        f'«{x}»' for x in selected
    )


def get_template(name):

    for template in templates:

        if template["name"] == name:

            return template

    return None


# -------------------------------------------------------
# Заголовок
# -------------------------------------------------------

st.title("📄 Генератор комментариев")

st.divider()


# -------------------------------------------------------
# Левая колонка
# -------------------------------------------------------

left, right = st.columns([1, 1.3])


with left:

    template_names = [
        t["name"]
        for t in templates
    ]

    selected_template = st.radio(
        "Причина отклонения",
        template_names
    )

    st.markdown("### Предметы")

    # -----------------------------------------
    # Чекбоксы предметов
    # -----------------------------------------

    col1, col2 = st.columns(2)

    selected_subjects = []

    half = (len(subjects) + 1) // 2

    left_subjects = subjects[:half]
    right_subjects = subjects[half:]

    with col1:
        for subject in left_subjects:
            if st.checkbox(subject, key=subject):
                selected_subjects.append(subject)

    with col2:
        for subject in right_subjects:
            if st.checkbox(subject, key=subject):
                selected_subjects.append(subject)


# -------------------------------------------------------
# Правая колонка
# -------------------------------------------------------

with right:

    st.markdown("## Комментарий")

    template = get_template(selected_template)

    comment = ""

    if template:

        if template["requires_subjects"]:

            if len(selected_subjects):

                comment = template["template"].replace(
                    "{SUBJECTS}",
                    format_subjects(selected_subjects)
                )

            else:
                st.info("Выберите хотя бы один предмет.")

        else:
            comment = template["template"]

    if comment:

        st.text_area(
            "Готовый комментарий",
            value=comment,
            height=150,
            key="comment_text"
        )

        st.components.v1.html(
    f"""
    <textarea id="comment" style="display:none;">{comment}</textarea>

    <button
        id="copyBtn"
        onclick="copyText()"
        style="
            width:100%;
            background:#ff4b4b;
            color:white;
            border:none;
            border-radius:8px;
            padding:12px;
            font-size:18px;
            cursor:pointer;
            transition:all .15s ease;
        ">
        📋 Копировать комментарий
    </button>

    <p id="msg"
       style="
            display:none;
            color:#4CAF50;
            font-weight:bold;
            margin-top:10px;
            text-align:center;">
        ✅ Комментарий успешно скопирован
    </p>

    <script>
    async function copyText(){{

        const btn = document.getElementById("copyBtn");

        btn.style.transform = "scale(0.97)";
        btn.style.opacity = "0.8";

        await navigator.clipboard.writeText(
            document.getElementById("comment").value
        );

        setTimeout(()=>{{
            btn.style.transform = "scale(1)";
            btn.style.opacity = "1";
        }},150);

        const msg = document.getElementById("msg");
        msg.style.display="block";

        setTimeout(()=>{{
            msg.style.display="none";
        }},2000);
    }}
    </script>
    """,
    height=90,
)

st.divider()

with st.sidebar:
    st.header("📌 Шпаргалка")
    st.caption("Минимальные баллы ЕГЭ")

    st.dataframe(
        df_scores,
        hide_index=True,
        use_container_width=True
    )


st.caption(
    "Генератор комментариев • Версия 1.0"
)