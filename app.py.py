import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import json
from calculator import sun_constellation

st.set_page_config(page_title="13 знаков Зодиака", layout="centered")
st.title("🔭 Астрономический калькулятор созвездий")
st.markdown("Введите дату и время рождения (UTC), чтобы узнать настоящее положение Солнца среди 13 зодиакальных созвездий и соответствующий архетип.")

col1, col2 = st.columns(2)
with col1:
    date = st.date_input("Дата", datetime.now().date())
with col2:
    time = st.time_input("Время", datetime.now().time())

if st.button("Рассчитать", type="primary"):
    dt = datetime.combine(date, time, tzinfo=pytz.UTC)
    with st.spinner("Вычисляем..."):
        code, arch = sun_constellation(dt)
    if code:
        st.success(f"Солнце в созвездии **{code}**")
        st.info(f"Архетип: **{arch}**")
        st.session_state['last'] = {'datetime': dt.isoformat(), 'code': code, 'archetype': arch}
    else:
        st.error("Не удалось определить созвездие.")

if 'last' in st.session_state:
    st.divider()
    st.subheader("📥 Экспорт")
    colj, colc = st.columns(2)
    res = st.session_state['last']
    colj.download_button("JSON", json.dumps(res, ensure_ascii=False, indent=2),
                         file_name=f"result_{date}.json", mime="application/json")
    df = pd.DataFrame([res])
    colc.download_button("CSV", df.to_csv(index=False).encode('utf-8'),
                         file_name=f"result_{date}.csv", mime="text/csv")

st.divider()
st.subheader("📁 Пакетная обработка")
uploaded = st.file_uploader("Загрузите CSV с колонкой 'datetime'", type='csv')
if uploaded:
    df_in = pd.read_csv(uploaded)
    if 'datetime' in df_in.columns:
        results = []
        prog = st.progress(0)
        for i, row in df_in.iterrows():
            dt = pd.to_datetime(row['datetime']).to_pydatetime()
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=pytz.UTC)
            code, arch = sun_constellation(dt)
            results.append({'datetime': dt.isoformat(), 'code': code, 'archetype': arch})
            prog.progress((i+1)/len(df_in))
        st.success("Готово!")
        df_out = pd.DataFrame(results)
        st.dataframe(df_out)
        st.download_button("Скачать все результаты (CSV)",
                           df_out.to_csv(index=False).encode('utf-8'),
                           file_name="batch_results.csv", mime="text/csv")
    else:
        st.error("Файл должен содержать колонку 'datetime'.")