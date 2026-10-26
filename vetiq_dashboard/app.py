"""VetIQ dashboard — Flask + Plotly.

Place this file in vetiq_dashboard/app.py, alongside templates/dashboard.html.
Expected inputs are in vetiq_dashboard/data/.
"""
from __future__ import annotations

import calendar
import json
import re
from functools import lru_cache
from pathlib import Path
from threading import Lock

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.utils
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CONSULTATION_FILE = DATA_DIR / "consultations_5year_combined.csv"
SUMMARY_FILE = DATA_DIR / "consultation_dashboard_summary.csv"
SARIMA_FILE = DATA_DIR / "sarima_forecast.csv"
BASKET_FILES = [DATA_DIR / f"Basket_{n}.csv" for n in (1, 2, 3)]

# Dashboard-only exploratory classification, NOT the validated modelling target.
TICK_PATTERN = re.compile(
    r"paralysis tick|tick paralysis|tick bite|tick bites|"
    r"tick attached|attached tick|tick removal|remove tick|"
    r"removed tick|tick clip|tick search|tick toxicosis|"
    r"tick toxicity|tick infestation|ticks attached",
    flags=re.IGNORECASE,
)
TEXT_COLUMNS = [
    "ItemServiceFeeName", "ExaminationTextString",
    "SummaryString", "SpecialInstructionString",
]
_summary_lock = Lock()


def prepare_consultation_summary():
    """Build a small monthly summary from a large CSV, in chunks.

    This counts source rows, not unique ConsultationKey values.
    """
    if not CONSULTATION_FILE.exists():
        raise FileNotFoundError(
            f"Missing {CONSULTATION_FILE}. Supply it or an existing "
            f"{SUMMARY_FILE.name} in the data folder."
        )
    required = ["ConsultationDate", "ClinicID", "ClinicPseudonym", "DataSource"] + TEXT_COLUMNS
    parts = []
    earliest = latest = None
    reader = pd.read_csv(
        CONSULTATION_FILE, usecols=lambda c: c in required,
        chunksize=100_000, dtype=str, low_memory=False,
    )
    for number, chunk in enumerate(reader, 1):
        for col in required:
            if col not in chunk:
                chunk[col] = ""
        dates = pd.to_datetime(chunk["ConsultationDate"], errors="coerce")
        valid = dates.notna()
        chunk = chunk.loc[valid].copy()
        dates = dates.loc[valid]
        if chunk.empty:
            continue
        earliest = dates.min() if earliest is None else min(earliest, dates.min())
        latest = dates.max() if latest is None else max(latest, dates.max())
        match = pd.Series(False, index=chunk.index)
        for col in TEXT_COLUMNS:
            match |= chunk[col].fillna("").str.contains(TICK_PATTERN, na=False)
        chunk["TickRows"] = match.astype("int64")
        chunk["TotalRows"] = 1
        chunk["DataSource"] = chunk["DataSource"].fillna("Unknown")
        chunk["ClinicID"] = chunk["ClinicID"].fillna("Unknown")
        chunk["ClinicKey"] = chunk["DataSource"] + " | " + chunk["ClinicID"]
        chunk["ClinicPseudonym"] = chunk["ClinicPseudonym"].fillna("Unknown").replace("", "Unknown")
        chunk["Month"] = dates.dt.to_period("M").astype(str)
        parts.append(chunk.groupby(
            ["ClinicKey", "ClinicPseudonym", "Month"], as_index=False
        )[["TotalRows", "TickRows"]].sum())
        if number % 10 == 0:
            print(f"Processed {number * 100_000:,} consultation rows")
    if not parts:
        raise ValueError("No consultation rows with valid dates")
    summary = pd.concat(parts, ignore_index=True).groupby(
        ["ClinicKey", "ClinicPseudonym", "Month"], as_index=False
    )[["TotalRows", "TickRows"]].sum()
    summary["DataStart"] = earliest.strftime("%Y-%m-%d")
    summary["DataEnd"] = latest.strftime("%Y-%m-%d")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    summary.to_csv(SUMMARY_FILE, index=False)
    return summary


@lru_cache(maxsize=1)
def load_consultation_summary():
    with _summary_lock:
        df = pd.read_csv(SUMMARY_FILE) if SUMMARY_FILE.exists() else prepare_consultation_summary()
        required = {"Month", "ClinicKey", "TotalRows", "TickRows"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Summary CSV missing columns: {sorted(missing)}")
        df["Month"] = pd.to_datetime(df["Month"], errors="coerce")
        df = df.dropna(subset=["Month"]).copy()
        df["Year"] = df["Month"].dt.year
        for col in ("TotalRows", "TickRows"):
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        return df


@lru_cache(maxsize=1)
def load_google_trends():
    baskets = []
    for i, file in enumerate(BASKET_FILES):
        if not file.exists():
            print(f"Optional Google Trends file missing: {file}")
            return pd.DataFrame()
        frame = pd.read_csv(file)
        if "Time" not in frame.columns:
            print(f"Google Trends file has no Time column: {file}")
            return pd.DataFrame()
        frame["Time"] = pd.to_datetime(frame["Time"], errors="coerce")
        frame = frame.dropna(subset=["Time"]).drop_duplicates(subset=["Time"])
        if i:
            frame = frame.drop(columns=["tick"], errors="ignore")
        baskets.append(frame.set_index("Time"))
    trends = pd.concat(baskets, axis=1, join="inner").sort_index()
    trends = trends.loc[:, ~trends.columns.duplicated()].reset_index().rename(columns={"Time": "Month"})
    trends = trends[trends["Month"].between("2020-01-01", "2026-10-01")].copy()
    terms = [col for col in trends.columns if col != "Month"]
    if not terms or trends.empty:
        return pd.DataFrame()
    z_columns = []
    for col in terms:
        values = pd.to_numeric(trends[col], errors="coerce")
        trends[col] = values
        std = values.std()
        z_col = f"{col}_z"
        trends[z_col] = (values - values.mean()) / std if pd.notna(std) and std > 0 else 0.0
        z_columns.append(z_col)
    trends["Search_Index_Z"] = trends[z_columns].mean(axis=1)
    lo, hi = trends["Search_Index_Z"].min(), trends["Search_Index_Z"].max()
    trends["Tick_Search_Index"] = (
        100 * (trends["Search_Index_Z"] - lo) / (hi - lo)
        if pd.notna(hi) and pd.notna(lo) and hi > lo else 0.0
    )
    trends["Year"] = trends["Month"].dt.year
    trends["Month_Num"] = trends["Month"].dt.month
    return trends


def _find_column(frame, candidates):
    lookup = {re.sub(r"[^a-z0-9]", "", str(c).lower()): c for c in frame.columns}
    for candidate in candidates:
        key = re.sub(r"[^a-z0-9]", "", candidate.lower())
        if key in lookup:
            return lookup[key]
    return None


@lru_cache(maxsize=1)
def load_sarima_forecast():
    """Read SARIMA output without assuming its precise exported column names."""
    if not SARIMA_FILE.exists():
        return pd.DataFrame(), f"SARIMA file not found: {SARIMA_FILE.name}"
    try:
        raw = pd.read_csv(SARIMA_FILE)
    except Exception as exc:
        return pd.DataFrame(), f"Could not read SARIMA CSV: {exc}"
    date_col = _find_column(raw, [
        "Week_End", "Forecast_Date", "Target_Date", "Date", "ds", "Month", "Time", "Unnamed: 0"
    ])
    prediction_col = _find_column(raw, [
        "Forecast", "SARIMA_Forecast", "Predicted", "Prediction", "Predicted_Tick_Consultations",
        "Predicted_Ticks", "yhat", "Mean_Forecast", "Forecast_Mean", "mean", "Predicted_Value"
    ])
    lower_col = _find_column(raw, ["Lower_CI", "CI_Lower", "Lower_Bound", "Lower_95", "Lower", "yhat_lower"])
    upper_col = _find_column(raw, ["Upper_CI", "CI_Upper", "Upper_Bound", "Upper_95", "Upper", "yhat_upper"])
    actual_col = _find_column(raw, ["Actual", "Observed", "Actual_Tick_Consultations", "Actual_Ticks", "y_true"])
    clinic_col = _find_column(raw, ["ClinicID", "Clinic_ID", "Clinic", "ClinicPseudonym"])
    if not date_col or not prediction_col:
        return pd.DataFrame(), (
            "SARIMA columns not recognised. Found: " + ", ".join(map(str, raw.columns))
            + ". Expected a date column and a forecast/prediction column."
        )
    df = pd.DataFrame({
        "Date": pd.to_datetime(raw[date_col], errors="coerce"),
        "Forecast": pd.to_numeric(raw[prediction_col], errors="coerce"),
    })
    if lower_col:
        df["Lower"] = pd.to_numeric(raw[lower_col], errors="coerce")
    if upper_col:
        df["Upper"] = pd.to_numeric(raw[upper_col], errors="coerce")
    if actual_col:
        df["Actual"] = pd.to_numeric(raw[actual_col], errors="coerce")
    if clinic_col:
        df["ClinicID"] = raw[clinic_col].astype(str)
    df = df.dropna(subset=["Date", "Forecast"]).sort_values("Date").reset_index(drop=True)
    if df.empty:
        return df, "SARIMA CSV has no usable dated forecast rows."
    return df, None


def chart_json(fig):
    fig.update_layout(
        template="plotly_white", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=45, r=20, t=45, b=50),
        font=dict(family="Arial", size=12), hovermode="x unified",
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def empty_chart(message):
    fig = go.Figure()
    fig.add_annotation(text=message, x=.5, y=.5, xref="paper", yref="paper", showarrow=False)
    fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False), height=320)
    return chart_json(fig)


def create_dashboard_figures(df):
    if df.empty:
        empty = empty_chart("No consultation data for this selection")
        return dict(weekly_graph=empty, season_graph=empty, clinic_graph=empty, yearly_graph=empty, peak_data=[])
    monthly = df.groupby("Month", as_index=False)[["TotalRows", "TickRows"]].sum().sort_values("Month")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly["Month"], y=monthly["TickRows"], mode="lines+markers",
                             name="Tick-related source rows", line=dict(color="#0f9f91", width=3)))
    fig.update_layout(title="Monthly tick-related activity", xaxis_title="Month", yaxis_title="Tick-related source rows")
    weekly_graph = chart_json(fig)  # Legacy template variable; chart is MONTHLY.

    seasonal = monthly.copy()
    seasonal["Year"] = seasonal["Month"].dt.year
    seasonal["Month_Num"] = seasonal["Month"].dt.month
    complete_years = seasonal.groupby("Year")["Month_Num"].nunique()
    complete_years = complete_years[complete_years == 12].index
    historical = seasonal[seasonal["Year"].isin(complete_years)]
    if historical.empty:
        season_graph = empty_chart("No complete calendar year in selection")
    else:
        average = historical.groupby("Month_Num")["TickRows"].mean().reindex(range(1, 13))
        fig = go.Figure(go.Bar(x=[calendar.month_abbr[i] for i in range(1, 13)],
                               y=average.values, marker_color="#667eea"))
        fig.update_layout(title="Average monthly seasonality", yaxis_title="Average tick-related source rows")
        season_graph = chart_json(fig)

    clinics = df.groupby("ClinicKey", as_index=False)["TickRows"].sum().nlargest(10, "TickRows").sort_values("TickRows")
    fig = go.Figure(go.Bar(x=clinics["TickRows"], y=clinics["ClinicKey"], orientation="h", marker_color="#0f9f91"))
    fig.update_layout(title="Top 10 source-specific clinic IDs", xaxis_title="Tick-related source rows")
    clinic_graph = chart_json(fig)

    yearly = df.groupby("Year", as_index=False)["TickRows"].sum()
    fig = go.Figure(go.Bar(x=yearly["Year"].astype(str), y=yearly["TickRows"], marker_color="#f59e0b"))
    fig.update_layout(title="Annual tick-related activity", yaxis_title="Tick-related source rows")
    yearly_graph = chart_json(fig)
    peaks = []
    for year, group in seasonal.groupby("Year"):
        peak = group.loc[group["TickRows"].idxmax()]
        peaks.append({"year": int(year), "month": peak["Month"].strftime("%B"),
                      "count": f"{int(peak['TickRows']):,}"})
    return dict(weekly_graph=weekly_graph, season_graph=season_graph,
                clinic_graph=clinic_graph, yearly_graph=yearly_graph, peak_data=peaks)


def create_google_chart(consultations, trends):
    if trends.empty or consultations.empty:
        return empty_chart("Google Trends or consultation data unavailable")
    monthly = consultations.groupby("Month", as_index=False)["TickRows"].sum()
    comparison = monthly.merge(trends[["Month", "Tick_Search_Index"]], on="Month", how="inner")
    if comparison.empty:
        return empty_chart("No overlapping Google Trends and consultation months")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=comparison["Month"], y=comparison["Tick_Search_Index"],
                             name="Google search index", line=dict(color="#4285f4", width=3)))
    fig.add_trace(go.Scatter(x=comparison["Month"], y=comparison["TickRows"],
                             name="Tick-related source rows", yaxis="y2", line=dict(color="#0f9f91", width=3)))
    fig.update_layout(title="Google search interest vs tick-related activity", xaxis_title="Month",
                      yaxis=dict(title="Google search index (0–100)"),
                      yaxis2=dict(title="Tick-related source rows", overlaying="y", side="right"),
                      legend=dict(orientation="h", y=-.3))
    return chart_json(fig)


def create_sarima_chart(forecasts):
    if forecasts.empty:
        return empty_chart("No SARIMA forecast data available")
    fig = go.Figure()
    if "Actual" in forecasts:
        fig.add_trace(go.Scatter(x=forecasts["Date"], y=forecasts["Actual"],
                                 name="Observed", mode="lines+markers", line=dict(color="#64748b")))
    if {"Lower", "Upper"}.issubset(forecasts.columns):
        fig.add_trace(go.Scatter(x=forecasts["Date"], y=forecasts["Upper"],
                                 mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=forecasts["Date"], y=forecasts["Lower"],
                                 mode="lines", fill="tonexty", fillcolor="rgba(15,159,145,0.15)",
                                 line=dict(width=0), name="Forecast interval"))
    fig.add_trace(go.Scatter(x=forecasts["Date"], y=forecasts["Forecast"],
                             name="SARIMA forecast", mode="lines+markers", line=dict(color="#0f9f91", width=3)))
    fig.update_layout(title="SARIMA forecast", xaxis_title="Forecast date", yaxis_title="Forecast value")
    return chart_json(fig)


def _filter_forecasts(forecasts, year="all", clinic="all"):
    if forecasts.empty:
        return forecasts
    result = forecasts
    if year != "all":
        try:
            result = result[result["Date"].dt.year == int(year)]
        except ValueError:
            pass
    # Consultation filter uses source-specific ClinicKey; forecast CSV may use ClinicID.
    # Only filter forecast if the IDs can be compared explicitly.
    if clinic != "all" and "ClinicID" in result.columns:
        clinic_id = clinic.split(" | ")[-1]
        result = result[result["ClinicID"] == clinic_id]
    return result


@app.route("/")
def dashboard():
    summary = load_consultation_summary()
    trends = load_google_trends()
    forecasts, forecast_error = load_sarima_forecast()
    selected_year = request.args.get("year", "all")
    selected_clinic = request.args.get("clinic", "all")
    filtered = summary.copy()
    if selected_year != "all":
        try:
            filtered = filtered[filtered["Year"] == int(selected_year)]
        except ValueError:
            selected_year = "all"
    if selected_clinic != "all":
        filtered = filtered[filtered["ClinicKey"] == selected_clinic]
    figures = create_dashboard_figures(filtered)
    total_tick = int(filtered["TickRows"].sum())
    total_rows = int(filtered["TotalRows"].sum())
    total_clinics = int(filtered["ClinicKey"].nunique())
    if filtered.empty:
        start_date = end_date = "N/A"
    elif selected_year == "all" and selected_clinic == "all" and {"DataStart", "DataEnd"}.issubset(filtered.columns):
        start_date, end_date = str(filtered["DataStart"].iloc[0]), str(filtered["DataEnd"].iloc[0])
    else:
        start_date = filtered["Month"].min().strftime("%d %b %Y")
        end_date = filtered["Month"].max().strftime("%b %Y")
    years = sorted(summary["Year"].dropna().unique().astype(int).tolist())
    clinics = sorted(summary["ClinicKey"].dropna().unique().tolist())
    selected_forecasts = _filter_forecasts(forecasts, selected_year, selected_clinic)
    sarima_graph = create_sarima_chart(selected_forecasts)
    return render_template(
        "dashboard.html",
        # Preserve existing template keys. These two legacy labels represent rows, NOT unique patients.
        total_consultations=total_tick,
        unique_patients=total_rows,
        total_clinics=total_clinics,
        start_date=start_date, end_date=end_date,
        weekly_graph=figures["weekly_graph"], season_graph=figures["season_graph"],
        clinic_graph=figures["clinic_graph"], yearly_graph=figures["yearly_graph"],
        peak_data=figures["peak_data"], google_timing=[],
        google_graph=create_google_chart(filtered, trends),
        years=years, clinics=clinics, selected_year=selected_year,
        selected_clinic=selected_clinic, total_rows=total_rows,
        total_tick_rows=total_tick,
        tick_percentage=round(total_tick / total_rows * 100, 2) if total_rows else 0,
        google_available=not trends.empty,
        sarima_graph=sarima_graph, forecast_graph=sarima_graph,
        sarima_available=not selected_forecasts.empty,
        sarima_error=forecast_error,
        sarima_rows=len(selected_forecasts),
        sarima_start=selected_forecasts["Date"].min().strftime("%d %b %Y") if not selected_forecasts.empty else "N/A",
        sarima_end=selected_forecasts["Date"].max().strftime("%d %b %Y") if not selected_forecasts.empty else "N/A",
    )


@app.route("/api/overview")
def api_overview():
    df = load_consultation_summary()
    return jsonify({
        "total_rows": int(df["TotalRows"].sum()),
        "tick_related_rows": int(df["TickRows"].sum()),
        "source_specific_clinics": int(df["ClinicKey"].nunique()),
        "note": "Row counts from preliminary dashboard screening; not distinct consultations",
    })


@app.route("/api/consultations/weekly")
def api_weekly():
    # Legacy route; the source summary is monthly, so return accurately named month keys.
    df = load_consultation_summary()
    monthly = df.groupby("Month", as_index=False)["TickRows"].sum()
    return jsonify([{"month": row.Month.strftime("%Y-%m"), "tick_related_rows": int(row.TickRows)}
                    for row in monthly.itertuples(index=False)])


@app.route("/api/clinics")
def api_clinics():
    df = load_consultation_summary()
    clinics = df.groupby("ClinicKey", as_index=False)["TickRows"].sum().sort_values("TickRows", ascending=False)
    return jsonify(clinics.to_dict(orient="records"))


@app.route("/api/google-trends")
def api_google_trends():
    trends = load_google_trends()
    if trends.empty:
        return jsonify([])
    return jsonify([{"month": row.Month.strftime("%Y-%m"),
                     "search_index": round(float(row.Tick_Search_Index), 2)}
                    for row in trends.itertuples(index=False)])


@app.route("/api/forecast/sarima")
def api_sarima():
    forecasts, error = load_sarima_forecast()
    if error:
        return jsonify({"available": False, "error": error, "data": []})
    rows = []
    for row in forecasts.to_dict(orient="records"):
        record = {"date": row["Date"].strftime("%Y-%m-%d"), "forecast": float(row["Forecast"])}
        for key in ("Lower", "Upper", "Actual"):
            if key in row:
                record[key.lower()] = float(row[key]) if pd.notna(row[key]) else None
        if "ClinicID" in row:
            record["clinic_id"] = row["ClinicID"]
        rows.append(record)
    return jsonify({"available": True, "rows": len(rows), "data": rows})


if __name__ == "__main__":
    print("VetIQ Dashboard")
    print("Dashboard folder:", BASE_DIR)
    print("Consultation summary exists:", SUMMARY_FILE.exists())
    print("Consultation CSV exists:", CONSULTATION_FILE.exists())
    print("SARIMA forecast exists:", SARIMA_FILE.exists())
    for file in BASKET_FILES:
        print(f"{file.name} exists: {file.exists()}")
    forecast, error = load_sarima_forecast()
    print("SARIMA status:", error or f"Loaded {len(forecast)} forecast rows")
    app.run(host="127.0.0.1", port=5001, debug=False, use_reloader=False)
