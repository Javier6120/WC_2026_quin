from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))


import streamlit as st, pandas as pd, plotly.express as px 
from database import engine

# Title + Leaderboard
st.title("🏆 Mundial Quiniela Familia Vega")
leaderboard_df = pd.read_sql(""" SELECT * FROM leaderboard  ORDER BY total_points DESC""",engine)
leaderboard_df.index = range(1, len(leaderboard_df) + 1)
st.table(leaderboard_df)

# Leader
col1, col2 = st.columns(2)
col1.metric("Participantes", len(leaderboard_df))
col2.metric("Líder", leaderboard_df.iloc[0]["name"])

# Predictions by Participants
pred_df = pd.read_sql("""SELECT date, name AS nombre, match_name AS partido, 
                                spa_pred AS predicción, outcome AS resultado,
                                points AS puntos 
                                FROM scored
                                ORDER BY date""",engine)
pred_df['date'] = (pd.to_datetime(pred_df['date'], utc=True)
                   .dt.tz_convert("America/Mexico_City")
                   .dt.strftime("%Y-%m-%d  |  %H:%M"))
participant = st.selectbox("Selecciona un participante", sorted(pred_df["nombre"].unique()))
participant_predictions = pred_df[pred_df["nombre"] == participant]
st.subheader(f"⚽ Predicciones de {participant}")
st.dataframe(participant_predictions, hide_index=True, use_container_width=True)