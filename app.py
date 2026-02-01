import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from urllib.parse import quote_plus

st.set_page_config(page_title="Global Seismic Trends", layout="wide")

st.title("🌍Global Seismic Trends: Data-Driven Earthquake Insights")
st.markdown("Earthquake Insights Dashboard 📊")

st.markdown(" ")
st.markdown("### 🔍 Select an analysis to explore insights")

query_option = st.selectbox(
    "",
    [
        "1.Top 10 strongest earthquakes (mag)",
        "2.Top 10 deepest earthquakes (depth_km)",
        "3.Shallow earthquakes < 50 km and mag > 7.5",
        "4.Average magnitude per magnitude type (magType)",
        "5.Year with most earthquakes",
        "6.Month with highest number of earthquakes",
        "7.Day of week with most earthquakes",
        "8.Count of earthquakes per hour of day",
        "9.Most active reporting network (net)",
        "10.Top 5 places with highest casualties",
        "11.Average economic loss by alert level",
        "12.Count of reviewed vs automatic earthquakes (status)",
        "13.Count by earthquake type (type)",
        "14.Number of earthquakes by data type (types)",
        "15.Events with high station coverage (nst > threshold)",
        "16.Number of tsunamis triggered per year",
        "17.Count earthquakes by alert levels(red, orange, etc.)",
        "18.Top 5 countries with the highest average magnitude of earthquakes in the past 10 years",
        "19.Countries that have experienced both shallow and deep earthquakes within the same month",
        "20.Year-over-year growth rate in the total number of earthquakes globally",
        "21.Top 3 most seismically active regions by combining both frequency and average magnitude",
        "22.Average depth of earthquakes in each country within ±5° latitude range of the equator",
        "23.Countries having the highest ratio of shallow to deep earthquakes",
        "24.Average magnitude difference between earthquakes with tsunami alerts and those without",
        "25.Identify events with the lowest data reliability using the gap & rms (highest average error margins)",
        "26.Regions with the highest frequency of deep-focus earthquakes (depth > 300 km)"
        
    ]
)

DB_USER = "root"
DB_PASSWORD = "Mohajaya@0706"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "earthquake_db1"

DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD)
DB_NAME_ENCODED = quote_plus(DB_NAME)

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD_ENCODED}@{DB_HOST}:{DB_PORT}/{DB_NAME_ENCODED}"
)


# Query function

def run_query(query):
    return pd.read_sql(query, engine)




queries = {
    "1.Top 10 strongest earthquakes (mag)": """
        SELECT id, place, mag,depth_km, time,country
        FROM earthquakes
        ORDER BY mag DESC
        LIMIT 10;
    """,

    "2.Top 10 deepest earthquakes (depth_km)": """
        SELECT id, place,mag,depth_km, time,country
        FROM earthquakes
        ORDER BY depth_km DESC
        LIMIT 10;
    """,

    "3.Shallow earthquakes < 50 km and mag > 7.5": """
        SELECT id, place, mag, depth_km,time,country
        FROM earthquakes
        WHERE depth_km < 50 AND mag > 7.5
        ORDER BY mag DESC;
    """,

    "4.Average magnitude per magnitude type (magType)": """
        SELECT magType,AVG(mag) AS avg_magnitude
        FROM earthquakes
        GROUP BY magType
        ORDER BY avg_magnitude DESC;
    """,

    "5.Year with most earthquakes": """
        SELECT year,COUNT(*) AS earthquake_count
        FROM earthquakes
        GROUP BY year
        ORDER BY earthquake_count DESC;
        
    """,
    
    "6.Month with highest number of earthquakes": """
        SELECT monthname(time) AS month,COUNT(*) AS earthquake_count
        FROM earthquakes
        GROUP BY monthname(
        ORDER BY earthquake_count DESC;
        
    """,
    
    "7.Day of week with most earthquakes": """
        SELECT day_of_week,COUNT(*) AS earthquake_count
        FROM earthquakes
        GROUP BY day_of_week
        ORDER BY FIELD(day_of_week,'Monday','Tuesday','Wednesday','Thursday',
           'Friday','Saturday','Sunday'
           );
        
    """,
    
    "8.Count of earthquakes per hour of day": """
        SELECT DATE_FORMAT(time,'%%H:00') AS hour_of_day,
        COUNT(*) AS earthquake_count
        FROM earthquakes
        GROUP BY DATE_FORMAT(time,'%%H:00'),
        HOUR(time)
        ORDER BY HOUR(time)
        LIMIT 10;
    """,
    
    "9.Most active reporting network (net)": """
       SELECT net,COUNT(*) AS report_count
       FROM earthquakes
       GROUP BY net
       ORDER BY report_count DESC
       LIMIT 10;
    """,

    "10.Top 5 places with highest casualties": """
       SELECT place,SUM(sig) AS total_impact_score
       FROM earthquakes
       GROUP BY place
       ORDER BY total_impact_score DESC
       LIMIT 5;
    """,

    "11.Average economic loss by alert level": """
       SELECT status,AVG(sig) AS avg_economic_impact
       FROM earthquakes
       GROUP BY status
       ORDER BY avg_economic_impact DESC
       LIMIT 5;
    """,

    "12.Count of reviewed vs automatic earthquakes (status)": """
        SELECT status,COUNT(*) AS total_earthquakes
        FROM earthquakes
        GROUP BY status
        ORDER BY total_earthquakes DESC;
    """,

    "13.Count by earthquake type (type)": """
        SELECT type,COUNT(*) AS total_earthquakes
        FROM earthquakes
        GROUP BY type;
    """,

    "14.Number of earthquakes by data type (types)": """
        SELECT types,COUNT(*) AS total_earthquakes
        FROM earthquakes
        GROUP BY types
        ORDER BY total_earthquakes DESC
        LIMIT 10;
    """,

    "15.Events with high station coverage (nst > threshold)": """
        SELECT * FROM earthquakes
        WHERE nst > 50
        LIMIT 10;
    """,

    "16.Number of tsunamis triggered per year": """
        SELECT year,COUNT(*) AS tsunami_events
        FROM earthquakes
        WHERE tsunami = 1
        GROUP BY year
        ORDER BY year;
    """,

    "17.Count earthquakes by alert levels(red, orange, etc.)": """
        SELECT
          CASE
            WHEN sig>=600 THEN 'red'
            WHEN sig>=400 THEN 'orange'
            WHEN sig>=200 THEN 'yellow'
            ELSE 'green'
          END AS alert_level,
          COUNT(*) AS total_earthquakes
        FROM earthquakes
        WHERE sig IS NOT NULL
        GROUP BY alert_level
        ORDER BY total_earthquakes DESC;
    """,

    "18.Top 5 countries with the highest average magnitude of earthquakes in the past 10 years": """
        SELECT place AS region,
        AVG(mag) AS avg_magnitude
        FROM earthquakes
        WHERE year >= YEAR(CURDATE()) - 10
        GROUP BY place
        ORDER BY avg_magnitude DESC
        LIMIT 5;
    """,

    "19.Countries that have experienced both shallow and deep earthquakes within the same month": """
        SELECT DISTINCT e1.country
        FROM earthquakes e1
        JOIN earthquakes e2
          ON e1.country = e2.country
          AND YEAR(e1.time) = YEAR(e2.time)
          AND MONTH(e1.time) = MONTH(e2.time)
        WHERE e1.depth_km < 70          -- shallow
           AND e2.depth_km > 300         -- deep
           AND e1.country IS NOT NULL
           AND e1.country <> ''
           AND e1.country <> 'Unknown'
           LIMIT 10;
        
    """,

    "20.Year-over-year growth rate in the total number of earthquakes globally": """
         WITH yearly_counts AS (
           SELECT YEAR(time) AS year,
           COUNT(*) AS total_earthquakes
           FROM earthquakes
           GROUP BY YEAR(time)
           ),
         growth_calc AS (
           SELECT  year,total_earthquakes,
             LAG(total_earthquakes) OVER (ORDER BY year) AS prev_year_count
            FROM yearly_counts
            )
         SELECT year,total_earthquakes,prev_year_count,
         ROUND(
           ((total_earthquakes - prev_year_count) / prev_year_count) * 100,2
           )
         AS yoy_growth_percent
         FROM growth_calc
         WHERE prev_year_count IS NOT NULL
         AND year < 2026   -- exclude incomplete year
         ORDER BY year;
    """,

    "21.Top 3 most seismically active regions by combining both frequency and average magnitude": """
         SELECT country,
         COUNT(*) AS frequency,
         AVG(mag) AS avg_magnitude,
         (COUNT(*) * AVG(mag)) AS seismic_score
         FROM earthquakes
         WHERE country IS NOT NULL AND country <> ''
         AND country<>'Unknown'
         GROUP BY country
         ORDER BY seismic_score DESC
         LIMIT 3;
    """,

    "22.Average depth of earthquakes in each country within ±5° latitude range of the equator": """
         SELECT country,
         AVG(depth_km) AS avg_depth_near_equator
         FROM earthquakes
         WHERE latitude BETWEEN -5 AND 5
         AND country IS NOT NULL
         AND country <> ''
         GROUP BY country
         ORDER BY avg_depth_near_equator DESC
         LIMIT 10;
    """,

    "23.Countries having the highest ratio of shallow to deep earthquakes": """
         SELECT country,
         SUM(CASE WHEN depth_km < 70 THEN 1 ELSE 0 END) AS shallow_count,
         SUM(CASE WHEN depth_km > 300 THEN 1 ELSE 0 END) AS deep_count,
         ROUND(
            SUM(CASE WHEN depth_km < 70 THEN 1 ELSE 0 END) /
            NULLIF(SUM(CASE WHEN depth_km > 300 THEN 1 ELSE 0 END), 0),
         2) AS shallow_deep_ratio
         FROM earthquakes
         WHERE country IS NOT NULL
          AND country <> ''
         GROUP BY country
         HAVING deep_count > 0
         ORDER BY shallow_deep_ratio DESC
         LIMIT 10;
    """,

    "24.Average magnitude difference between earthquakes with tsunami alerts and those without": """
         SELECT
         CASE
          WHEN tsunami=1 THEN 'Tsunami'
          ELSE 'Non-Tsunami'
          END AS tsunami_flag,
         AVG(mag) AS avg_magnitude,
         COUNT(*) AS total_events
         FROM earthquakes
         GROUP BY tsunami_flag;
    """,

    "25.Identify events with the lowest data reliability using the gap & rms (highest average error margins)": """
         SELECT
           id,
           place,
           gap,
           rms,
           (gap+rms) AS error_score
           FROM earthquakes
           WHERE gap IS NOT NULL OR rms IS NOT NULL
           ORDER BY error_score DESC
           LIMIT 20;
    """,
             
    "26.Regions with the highest frequency of deep-focus earthquakes (depth > 300 km)": """
         SELECT country AS region,
         COUNT(*) AS deep_focus_events,
         AVG(depth_km) AS avg_depth_km,
         AVG(mag) AS avg_magnitude
         FROM earthquakes
         WHERE depth_km > 300
         AND country IS NOT NULL
         AND country <> ''
         AND country <> 'Unknown'
         GROUP BY country
         ORDER BY deep_focus_events DESC
         LIMIT 10;
    """
}

# Run query

query = queries[query_option]
df = run_query(query)


# KPI 

st.markdown("## 📊 Key Earthquake Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("🌍 Total Records", len(df))

if "mag" in df.columns:
    col2.metric("📈 Max Magnitude", round(df["mag"].max(), 2))
    col3.metric("📉 Avg Magnitude", round(df["mag"].mean(), 2))
else:
    col2.metric("📈 Max Magnitude", "-")
    col3.metric("📉 Avg Magnitude", "-")

if "depth_km" in df.columns:
    col4.metric("🌊 Avg Depth (km)", round(df["depth_km"].mean(), 2))
else:
    col4.metric("🌊 Avg Depth (km)", "-")


# Matplotlib Visualization

st.markdown("##  Matplotlib Visualization")

numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()

if len(numeric_cols) >= 2:

    x_col = numeric_cols[0]
    y_col = numeric_cols[1]

    st.markdown(f"### 📈 {y_col.replace('_',' ').title()} vs {x_col.replace('_',' ').title()}")

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(df[x_col], df[y_col], marker='o', linestyle='-')

    ax.set_xlabel(x_col.replace("_", " ").title())
    ax.set_ylabel(y_col.replace("_", " ").title())
    ax.set_title(f"{y_col.replace('_',' ').title()} Analysis", fontsize=13, fontweight="bold")

    ax.grid(True, linestyle=":", alpha=0.3)

    st.pyplot(fig)

else:
    st.info("📊 Not enough numeric data available for visualization")

# Data Display

st.markdown("## 📋 Query Results")
st.dataframe(df,use_container_width=True,hide_index=True)



st.markdown("---")
st.markdown("### 🌍 Global Seismic Trends Dashboard")
st.markdown("Created by Mohana Selvi | Data-Driven Analytics Project")
