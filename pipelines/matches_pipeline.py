"""
matches_pipeline.py 

ETL pipeline responsible for loading the World Cup match
schedule and teams table into PostgreSQL(Neon DB).

Request match schedule from API Football.

Load CSV data, teams tables (ID, english/spanish names) 
and matches with IDs used in google forms.

Performs cleaning, transform dataset, and stores in 
PostgreSQL.

Source: 
    wc_matches.csv
    wc_teams.csv
    Football API 

Target Tables:
    matches (Neon DB)
    teams (Neon DB)
"""

import pandas as pd, sqlalchemy, requests
from database import engine
from config import token_1, DATA_DIR

def extract():
    """
    Extract matches data from Football API and 
    CSV Files.

    Returns:
        api_matches_df, file_matches_df, teams_df
            - pandas.Dataframe: Matches Api Data
            - pandas.Dataframe: Matches CSV Data
            - pandas.Dataframe: Teams CSV Data

    """
    # Request data from API
    token = {'X-Auth-Token':token_1}
    response = requests.get("https://api.football-data.org/v4/competitions/WC/matches", headers= token)
    json_data = response.json() 
    api_matches_df= pd.json_normalize(data=json_data['matches'])

    # Reads CSV with matches
    file_matches_df = pd.read_csv(DATA_DIR/'wc_matches.csv')
    # Reads CSV with names ids and eng/spa names
    teams_df = pd.read_csv(DATA_DIR/'wc_teams.csv')

    return api_matches_df, file_matches_df, teams_df


def transform(api_matches_df, file_matches_df, teams_df):
    """
    Prepares dataset for loading into PostgreSQL.
    Selects and renames columns.
    Merges to add teams IDs to matches.
    
    Args:
        api_matches_df 
            - pandas.Dataframe: Matches Api Data
        file_matches_df
            - pandas.Dataframe: Matches CSV Data
        teams_df
            - pandas.Dataframe: Teams CSV Data

    Returns: 
        new_matches_df
            - pandas.Dataframe: Cleaned and transformed dataset.

    """
    api_matches_df = api_matches_df[['id', 'utcDate', 'homeTeam.name','awayTeam.name', 'score.winner', 'stage']]
    api_matches_df.rename(columns={'id':'api_match_id', 'score.winner':'result','utcDate':'date'}, inplace=True)

    # Inner Join 
    matches_df = (pd.merge(file_matches_df, api_matches_df, 
                          left_on=['home_team', 'away_team','stage'], 
                          right_on=['homeTeam.name', 'awayTeam.name','stage'], how='inner')
                          .drop(columns=['homeTeam.name','awayTeam.name']))

    matches_df_ids = (pd.merge(matches_df, teams_df[['team_id','eng_team']],
                          left_on=['home_team'], 
                          right_on=['eng_team'], how='left')
                          .drop(columns=['eng_team','home_team'])
                          .rename(columns={'team_id':'home_team_id'}))
    
    matches_df_ids = (pd.merge(matches_df_ids, teams_df[['team_id','eng_team']],
                          left_on=['away_team'], 
                          right_on=['eng_team'], how='left')
                          .drop(columns=['eng_team','away_team'])
                          .rename(columns={'team_id':'away_team_id'}))
    
    # Leave only unregistered matches
    existing = pd.read_sql("SELECT forms_match_id FROM matches",engine)['forms_match_id']
    new_matches_df = matches_df_ids[~matches_df_ids['forms_match_id'].isin(existing)]
    return new_matches_df


def load(matches_df, teams_df):
    """
    Load transformed match data into PostgreSQL.
    Writes the prepared datasets to 'matches' and 'teams' tables.

    Args: 
        matches_df
            - pandas.Dataframe: Cleaned and transformed dataset.
        teams_df
            - pandas.Dataframe: Teams CSV data

    """
    if len(pd.read_sql("SELECT * FROM teams",engine))==0:
        print('Loading teams_df')
        teams_df.to_sql(name='teams',
                        con=engine,
                        if_exists = 'append',
                        index=False)
    
    print(f'Loading matches_df')
    matches_df.to_sql(name='matches',
              con= engine,
              if_exists = 'append',
              index= False)

# Extract
api_matches_df, file_matches_df, teams_df = extract()
print(f'Succesfull extraction: {len(api_matches_df)} matches')
# Transform
matches_df = transform(api_matches_df, file_matches_df, teams_df)
print(f'Matches to load: {len(matches_df)} matches')
# Load
load(matches_df,teams_df)
print('Loaded succesfully')

