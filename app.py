import streamlit as st
import plotly.graph_objects as go
from src.fetcher import fetch_realtime_weather
from src.analyzer import load_baseline, analyze_metrics
from src.advisor import generate_orchard_advisories

st.set_page_config(
    page_title="極端天氣分析系統｜果園氣象決策輔助",
    page_icon="🌦️",
    layout="wide",
)

st.title("🌦️ 極端天氣分析系統：果園微氣候與決策輔助平台")
st.caption("第七組專題實作｜串接中央氣象署 Open Data API，比對即時觀測與歷年同期氣候基準")

baseline_df = load_baseline("data/historical_baseline.csv")
stations_meta = (
    baseline_df[["station_id", "station_name", "county", "town"]]
    .drop_duplicates()
    .to_dict("records")
)

with st.sidebar:
    st.header("📍 果園測站與參數設定")
    station_labels = {
        f"{s['county']}{s['town']} ({s['station_name']}測站 - {s['station_id']})": s["station_id"]
        for s in stations_meta
    }
    selected_label = st.selectbox("選擇鄰近氣象站", list(station_labels.keys()))
    selected_station_id = station_labels[selected_label]

    realtime_data = fetch_realtime_weather(selected_station_id)
    st.info(f"資料來源：{realtime_data['source']}\n\n觀測時間：{realtime_data['obs_time']}")

    st.divider()
    st.subheader("🧪 當月累積指標輸入（可調整測試極端情境）")
    mtd_avg_temp = st.slider(
        "本月至今平均氣溫 (°C)",
        min_value=5.0,
        max_value=35.0,
        value=float(realtime_data["air_temp"]),
        step=0.1,
    )
    mtd_cum_rain = st.slider(
        "本月至今累積雨量 (mm)",
        min_value=0.0,
        max_value=600.0,
        value=float(realtime_data["daily_rain"]),
        step=1.0,
    )
    realtime_data["max_temp"] = st.number_input(
        "今日最高溫 (°C)", value=float(realtime_data["max_temp"]), step=0.5
    )
    realtime_data["min_temp"] = st.number_input(
        "今日最低溫 (°C)", value=float(realtime_data["min_temp"]), step=0.5
    )

analysis = analyze_metrics(
    realtime=realtime_data,
    baseline_df=baseline_df,
    mtd_avg_temp=mtd_avg_temp,
    mtd_cum_rain=mtd_cum_rain,
)
advisories = generate_orchard_advisories(analysis)

st.subheader(f"📊 {analysis['month']} 月氣候指標即時對照（截至本月第 {analysis['day_of_month']} 日）")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label=f"月均溫對照（{analysis['temp_status']}）",
        value=f"{analysis['mtd_avg_temp']} °C",
        delta=f"{analysis['temp_diff']:+.2f} °C (歷年同期 {analysis['hist_avg_temp']} °C)",
        delta_color="inverse",
    )

with col2:
    st.metric(
        label=f"累積雨量比（{analysis['rain_status']}）",
        value=f"{analysis['mtd_cum_rain']} mm ({analysis['rain_ratio']}%)",
        delta=f"同期應有基準 {analysis['expected_mtd_rain']} mm",
    )

with col3:
    st.metric(
        label=f"日夜溫差 DTR（{analysis['dtr_status']}）",
        value=f"{analysis['current_dtr']} °C",
        delta=f"{analysis['dtr_diff']:+.2f} °C (歷年平均溫差 {analysis['hist_dtr']} °C)",
    )

st.divider()

chart_col, advice_col = st.columns([1.15, 1])

with chart_col:
    st.subheader("📈 即時觀測 vs. 歷年同期基準比較")
    fig = go.Figure(
        data=[
            go.Bar(
                name="當期實測值",
                x=["月均溫 (°C)", "同期累積雨量 (mm)", "日夜溫差 (°C)"],
                y=[
                    analysis["mtd_avg_temp"],
                    analysis["mtd_cum_rain"],
                    analysis["current_dtr"],
                ],
                marker_color="#2E86AB",
            ),
            go.Bar(
                name="歷年同期基準",
                x=["月均溫 (°C)", "同期累積雨量 (mm)", "日夜溫差 (°C)"],
                y=[
                    analysis["hist_avg_temp"],
                    analysis["expected_mtd_rain"],
                    analysis["hist_dtr"],
                ],
                marker_color="#A3B18A",
            ),
        ]
    )
    fig.update_layout(
        barmode="group",
        height=380,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)

with advice_col:
    st.subheader("🌱 果園田間管理與防護行動建議")
    for item in advisories:
        content = f"**【{item['category']}】{item['title']}**\n\n{item['action']}"
        if item["level"] == "danger":
            st.error(content, icon="🚨")
        elif item["level"] == "warning":
            st.warning(content, icon="⚠️")
        elif item["level"] == "info":
            st.info(content, icon="💡")
        else:
            st.success(content, icon="✅")