# World Cup Pool

Proyecto de quiniela para el Mundial 2026.

## Tecnologías

- Python
- PostgreSQL
- SQLAlchemy
- Google Forms API

## Arquitectura

  			   Python
                              │
                              ▼
Google Sheets API ──► Predictions Pipeline
                              │
Football API     ───► Matches Pipeline
                              │
                              ▼
                         PostgreSQL
                              │
                              ▼
Football API    ──► Update Results Pipeline
                              │
                              ▼
                      Scoring Pipeline
                              │
                              ▼
                        Leaderboard
                              │
                              ▼
                     Streamlit Dashboard