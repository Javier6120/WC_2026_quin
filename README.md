# World Cup Pool

A web application for managing and tracking FIFA World Cup 2026 predictions. 
      
      - Participants submit match predictions via Google Forms.
      
      - Results are automatically updated from API-Football and predictions are scored after every result update. 
      
      - Leaderboard, participant predicitons and map of correct answers are displayed through an interactive dashboard (Streamlit).

## Features

- PostgreSQL database hosted on NeonDB.

- Scheduled updates via GitHub Actions.

      - Automated match result updates from API-Football.

      - Automated scoring pipeline.

- Streamlit web dashboard.

      - Leaderboard rankings.

      - Participant prediction explorer.

      - Correct predictions map.

## Tech Stack 

Data Engineering
- Python
- Pandas
- PostgreSQL
- SQLAlchemy

Infrastructure
- Neon Database
- GitHub Actions
- GitHub

Frontend
- Streamlit Community Cloud

Data Source
- SportsDB API
- Google Sheets API

## Project Architecture
![architecture](assets/architecture.png)

## Database schema
![db_schema](assets/postgre_tables.png)

## Streamlit App Screenshots
Screenshots use anonymized participant names for privacy.

### Leaderboard
![leaderboard](assets/lb.png)

### Predictions by participants
![predictions_by_participants](assets/preds.png)

### Map of correct predictions
![correct_predictions_map](assets/map.png)
