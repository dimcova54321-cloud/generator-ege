import json
import streamlit as st
import pyperclip
from pathlib import Path


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

st.caption(
    "Приемная комиссия"
)

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
            height=180
        )

        c1, c2 = st.columns(2)

        with c1:
            if st.button("📋 Копировать", use_container_width=True):
                pyperclip.copy(comment)
                st.success("Комментарий скопирован в буфер обмена.")

        with c2:
            if st.button("🧹 Очистить", use_container_width=True):

                # Снимаем все галочки
                for subject in subjects:
                    if subject in st.session_state:
                        st.session_state[subject] = False

                st.rerun()

    else:
        st.write("")

st.divider()

st.caption(
    "Генератор комментариев • Версия 1.0"
)

st.divider()

st.subheader("📌 Минимальные баллы ЕГЭ")

table = []

for subject, values in scores.items():
    table.append({
        "Предмет": subject,
        "Бюджет": values["Бюджет"],
        "Договор": values["Договор"]
    })

st.table(table)