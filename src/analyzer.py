import calendar
from datetime import datetime
import pandas as pd


def load_baseline(csv_path: str = "data/historical_baseline.csv") -> pd.DataFrame:
    return pd.read_csv(csv_path)


def analyze_metrics(
    realtime: dict,
    baseline_df: pd.DataFrame,
    mtd_avg_temp: float,
    mtd_cum_rain: float,
    target_date: datetime | None = None,
) -> dict:
    now = target_date or datetime.now()
    month = now.month
    days_in_month = calendar.monthrange(now.year, month)[1]
    day_ratio = max(now.day / days_in_month, 1 / days_in_month)

    row = baseline_df[
        (baseline_df["station_id"] == realtime["station_id"])
        & (baseline_df["month"] == month)
    ]

    if row.empty:
        hist_temp, hist_month_rain, hist_dtr = 22.0, 100.0, 9.0
    else:
        record = row.iloc[0]
        hist_temp = float(record["avg_temp"])
        hist_month_rain = float(record["avg_rain"])
        hist_dtr = float(record["avg_dtr"])

    expected_mtd_rain = round(hist_month_rain * day_ratio, 1)
    temp_diff = round(mtd_avg_temp - hist_temp, 2)
    rain_ratio = round((mtd_cum_rain / expected_mtd_rain) * 100, 1) if expected_mtd_rain > 0 else 100.0

    current_dtr = round(realtime["max_temp"] - realtime["min_temp"], 2)
    dtr_diff = round(current_dtr - hist_dtr, 2)

    if temp_diff >= 2.0:
        temp_status = "異常偏暖"
    elif temp_diff <= -2.0:
        temp_status = "異常偏冷"
    else:
        temp_status = "氣溫正常"

    if rain_ratio >= 150.0:
        rain_status = "雨量暴增"
    elif rain_ratio <= 50.0:
        rain_status = "乾旱偏少"
    else:
        rain_status = "雨量正常"

    if current_dtr >= 12.0:
        dtr_status = "溫差劇烈"
    elif current_dtr <= 5.0:
        dtr_status = "溫差偏小"
    else:
        dtr_status = "溫差適中"

    return {
        "month": month,
        "day_of_month": now.day,
        "mtd_avg_temp": mtd_avg_temp,
        "hist_avg_temp": hist_temp,
        "temp_diff": temp_diff,
        "temp_status": temp_status,
        "mtd_cum_rain": mtd_cum_rain,
        "expected_mtd_rain": expected_mtd_rain,
        "hist_month_rain": hist_month_rain,
        "rain_ratio": rain_ratio,
        "rain_status": rain_status,
        "current_dtr": current_dtr,
        "hist_dtr": hist_dtr,
        "dtr_diff": dtr_diff,
        "dtr_status": dtr_status,
    }