import pandas as pd, sqlalchemy, requests
from database import engine
from config import token_1

def extract():
    # Requests matches to Football-Data API
    token = {'X-Auth-Token':token_1}
    response = requests.get("https://api.football-data.org/v4/competitions/WC/matches", headers= token)
    json_data = response.json() 
    api_matches_df= pd.json_normalize(data=json_data['matches'])

    # Reads CSV with matches, mapped to forms_match_id's
    file_matches_df = pd.read_csv('wc_matches.csv')
    return api_matches_df, file_matches_df


def transform(api_matches_df, file_matches_df):
    # Selects specific columns from group stage matches
    api_matches_df = api_matches_df[api_matches_df['stage']=='GROUP_STAGE']
    api_matches_df = api_matches_df[['id', 'utcDate', 'homeTeam.name','awayTeam.name', 'score.winner']]
    api_matches_df.rename(columns={'id':'api_match_id', 'score.winner':'result','utcDate':'date'}, inplace=True)

    # Inner Join 
    matches_df = pd.merge(file_matches_df, api_matches_df, 
                          left_on=['home_team', 'away_team'], 
                          right_on=['homeTeam.name', 'awayTeam.name'], how='inner')

    matches_df.drop(columns=['homeTeam.name','awayTeam.name'],inplace=True)
    return matches_df


def load(DF):
    with engine.begin() as conn:
        conn.execute(sqlalchemy.text("TRUNCATE TABLE predictions, matches, participants"))
    DF.to_sql(name='matches',
              con= engine,
              if_exists = 'append',
              index= False)

api_matches_df, file_matches_df = extract()
matches_df = transform(api_matches_df, file_matches_df)
load(matches_df)

