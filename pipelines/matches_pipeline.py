"""
matches_pipeline.py 

ETL pipeline responsible for loading the World Cup match
schedule into PostgreSQL.

Requests match schedule from API Football and CSV file. 

Performs cleaning and transformation, and stores the data in 
PostgreSQL.

Source: 
    wc_matches.csv 
    Football API 

Target Table:
    matches
"""

import pandas as pd, sqlalchemy, requests
from database import engine
from config import token_1, DATA_DIR

def extract():
    """
    Extract matches data from Football API and 
    CSV File (contains match_id used in google forms).

    Returns:
        api_matches_df, file_matches_df
            - pandas.Dataframe: Matches Api Data
            - pandas.Dataframe: Matches CSV Data

    """
    # Request data from API
    token = {'X-Auth-Token':token_1}
    response = requests.get("https://api.football-data.org/v4/competitions/WC/matches", headers= token)
    json_data = response.json() 
    api_matches_df= pd.json_normalize(data=json_data['matches'])

    # Reads CSV with matches
    file_matches_df = pd.read_csv(DATA_DIR/'wc_matches.csv')
    return api_matches_df, file_matches_df


def transform(api_matches_df, file_matches_df):
    """
    Filters matches of group stage, sets column names 
    and merges API results and CSV results. 
    Prepares dataset for loading into PostgreSQL.

    Args:
        api_matches_df 
            - pandas.Dataframe: Matches Api Data
        file_matches_df
            - pandas.Dataframe: Matches CSV Data

    Returns: 
        matches_df
            - pandas.Dataframe: Cleaned and transformed dataset.

    """
    api_matches_df = api_matches_df[['id', 'utcDate', 'homeTeam.name','awayTeam.name', 'score.winner', 'stage']]
    api_matches_df.rename(columns={'id':'api_match_id', 'score.winner':'result','utcDate':'date'}, inplace=True)

    # Inner Join 
    matches_df = pd.merge(file_matches_df, api_matches_df, 
                          left_on=['home_team', 'away_team','stage'], 
                          right_on=['homeTeam.name', 'awayTeam.name','stage'], how='inner')
    
    matches_df.drop(columns=['homeTeam.name','awayTeam.name'],inplace=True)

    # Leave only unregistered matches
    existing = pd.read_sql("SELECT forms_match_id FROM matches",engine)['forms_match_id']
    new_matches_df = matches_df[~matches_df['forms_match_id'].isin(existing)]
    return new_matches_df


def load(DF):
    """
    Load transformed match data into PostgreSQL.
    Writes the prepared dataset to 'matches' table.

    Args: 
        matches_df
            - pandas.Dataframe: Cleaned and transformed dataset.

    """
    print(f'Loading:{DF['forms_match_id']}')
    DF.to_sql(name='matches',
              con= engine,
              if_exists = 'append',
              index= False)

api_matches_df, file_matches_df = extract()
print(f'Succesfull extraction: {len(api_matches_df)} matches')
matches_df = transform(api_matches_df, file_matches_df)
print(f'Matches to load: {len(matches_df)} matches')
load(matches_df)

