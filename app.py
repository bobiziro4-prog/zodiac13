import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import json
from calculator import sun_constellation

# ------------------------- Мультиязычность -------------------------
LANG = {
    'ru': {
        'title': '🔭 Астрономический калькулятор созвездий',
        'description': 'Введите дату и время рождения (UTC), чтобы узнать настоящее положение Солнца среди 13 зодиакальных созвездий и соответствующий архетип.',
        'date_label': 'Дата',
        'time_label': 'Время',
        'calculate': 'Рассчитать',
        'calculating': 'Вычисляем...',
        'success': 'Солнце в созвездии **{}**',
        'archetype': 'Архетип: **{}**',
        'error': 'Не удалось определить созвездие.',
        'export_header': '📥 Экспорт',
        'export_json': 'JSON',
        'export_csv': 'CSV',
        'batch_header': '📁 Пакетная обработка',
        'batch_upload': 'Загрузите CSV с колонкой \'datetime\'',
        'batch_error': 'Файл должен содержать колонку \'datetime\'.',
        'batch_success': 'Готово!',
        'batch_download': 'Скачать все результаты (CSV)',
        'language': 'Язык / Language',
    },
    'en': {
        'title': '🔭 Astronomical Constellation Calculator',
        'description': 'Enter your birth date and time (UTC) to find the true astronomical position of the Sun among the 13 zodiac constellations and the corresponding archetype.',
        'date_label': 'Date',
        'time_label': 'Time',
        'calculate': 'Calculate',
        'calculating': 'Calculating...',
        'success': 'Sun in constellation **{}**',
        'archetype': 'Archetype: **{}**',
        'error': 'Could not determine constellation.',
        'export_header': '📥 Export',
        'export_json': 'JSON',
        'export_csv': 'CSV',
        'batch_header': '📁 Batch processing',
        'batch_upload': 'Upload CSV with column \'datetime\'',
        'batch_error': 'File must contain \'datetime\' column.',
        'batch_success': 'Done!',
        'batch_download': 'Download all results (CSV)',
        'language': 'Language',
    }
}

st.set_page_config(page_title="13 Zodiac Signs" if st.session_state.get('lang', 'en') == 'en' else "13 знаков Зодиака", layout="centered")

# Выбор языка в боковой панели
lang = st.sidebar.selectbox(
    LANG['ru']['language'] if 'lang' not in st.session_state else LANG[st.session_state.lang]['language'],
    ['en', 'ru'],
    format_func=lambda x: 'English' if x == 'en' else 'Русский',
    key='lang'
)

texts = LANG[lang]

# Основной заголовок
st.title(texts['title'])
st.markdown(texts['description'])

# Ввод даты и времени
col1, col2 = st.columns(2)
with col1:
    date = st.date_input(
        texts['date_label'],
        value=datetime.now().date(),
        min_value=datetime(1950, 1, 1).date(),
        max_value=datetime(2050, 12, 31).date()
    )
with col2:
    time = st.time_input(texts['time_label'], datetime.now().time())

# Кнопка расчёта
if st.button(texts['calculate'], type="primary"):
    dt = datetime.combine(date, time, tzinfo=pytz.UTC)
    with st.spinner(texts['calculating']):
        code, arch = sun_constellation(dt)
    if code:
        st.success(texts['success'].format(code))
        st.info(texts['archetype'].format(arch))
        st.session_state['last'] = {'datetime': dt.isoformat(), 'code': code, 'archetype': arch}
    else:
        st.error(texts['error'])

# Экспорт одиночного результата
if 'last' in st.session_state:
    st.divider()
    st.subheader(texts['export_header'])
    colj, colc = st.columns(2)
    res = st.session_state['last']
    colj.download_button(
        texts['export_json'],
        json.dumps(res, ensure_ascii=False, indent=2),
        file_name=f"result_{date}.json",
        mime="application/json"
    )
    df = pd.DataFrame([res])
    colc.download_button(
        texts['export_csv'],
        df.to_csv(index=False).encode('utf-8'),
        file_name=f"result_{date}.csv",
        mime="text/csv"
    )

# Пакетная обработка
st.divider()
st.subheader(texts['batch_header'])
uploaded = st.file_uploader(texts['batch_upload'], type='csv')
if uploaded:
    df_in = pd.read_csv(uploaded)
    if 'datetime' in df_in.columns:
        results = []
        prog = st.progress(0)
        total = len(df_in)
        for i, row in df_in.iterrows():
            dt = pd.to_datetime(row['datetime']).to_pydatetime()
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=pytz.UTC)
            code, arch = sun_constellation(dt)
            results.append({'datetime': dt.isoformat(), 'code': code, 'archetype': arch})
            prog.progress((i + 1) / total)
        st.success(texts['batch_success'])
        df_out = pd.DataFrame(results)
        st.dataframe(df_out)
        st.download_button(
            texts['batch_download'],
            df_out.to_csv(index=False).encode('utf-8'),
            file_name="batch_results.csv",
            mime="text/csv"
        )
    else:
        st.error(texts['batch_error'])