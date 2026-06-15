"""
predictions_pipeline.py

ETL pipeline responsible for loading participant and predictions 
data into PostgreSQL(Neon DB).

Request data from Google Sheets API and read 'teams' tables.

Performs cleaning, transform dataset, and stores in 
PostgreSQL.

Source: 
    Google Sheets API
    teams (Neon DB) 

Target Tables:
    participants (Neon DB)
    predictions (Neon DB)
"""

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import pandas as pd, sqlalchemy 
from database import engine
from config import sheet_id, DATA_DIR, CREDENTIALS_DIR, name_map

def extract(): 
    """
    Extract predictions data from Google Sheets API. 

    Returns: 
        predictions_DF,teams_df
            - pandas.Dataframe: Predictions Sheets Data
            - pandas.Dataframe: Teams table
    
    """
    # Google Services Presmissions
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

    # Authentication
    creds = Credentials.from_service_account_file(CREDENTIALS_DIR/'credentials.json', scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds)

    # API Request
    form_entries = service.spreadsheets().values().get(spreadsheetId=sheet_id, 
                                                       range="Respuestas de formulario 1").execute()
    predictions_DF = pd.DataFrame(form_entries['values'][1:], columns=form_entries['values'][0])

    # Read teams table from PostgreSQL
    teams_df = pd.read_sql("SELECT * FROM teams",engine)
    return predictions_DF,teams_df


def transform(predictions_df, teams_df):
    """
    Prepares dataset for loading into PostgreSQL.
    Cleans data and converts wide format to long format.  
    Generates dataframe with participants data.

    Args:
        predictions_df
            - pandas.Dataframe: Predictions G-Sheets Data
        teams_df
            - pandas.Dataframe: Teams table
    Returns: 
        predictions_df
            - pandas.Dataframe: Predictions Data
        participants_df
            - pandas.Dataframe: Participants Data
        
    """
    name_map_dict = name_map
    # Cleaning names column
    predictions_df['Nombre'] = predictions_df['Nombre'].str.strip()
    predictions_df['Nombre'] = predictions_df['Nombre'].str.title()
    predictions_df['Nombre'] = predictions_df['Nombre'].replace(name_map_dict)
    predictions_df.rename(columns={'Nombre':'participant'}, inplace=True)
    predictions_df.drop(columns=['Marca temporal'],inplace=True)
    
    # Melt columns into rows 
    predictions_df = predictions_df.melt(id_vars='participant',
                                         var_name='forms_match_id',
                                         value_name='pred')
    
    # Fix name error from Google Forms
    predictions_df['pred'] = predictions_df['pred'].replace('Bosnia Herzegovina','Bosnia Herzegobina')
    
    # Merges to add IDs and teams names in english 
    predictions_df = pd.merge(predictions_df,teams_df,
                              left_on='pred',
                              right_on='spa_team',
                              how='left').drop(columns=['spa_team','team_id'])

    predictions_df['eng_team'] = predictions_df['eng_team'].fillna('Draw')
    predictions_df.rename(columns={'eng_team':'eng_pred', 'pred':'spa_pred'}, inplace=True)

    # Assign id to each participant
    participants_df = pd.DataFrame(predictions_df['participant'].unique(),columns=['name'])
    participants_df.reset_index(names='participant_id',inplace=True)

    predictions_df = pd.merge(participants_df,predictions_df,
                              left_on='name',
                              right_on='participant',
                              how='right').drop(columns=['participant','name'])

    return predictions_df, participants_df


def load(predictions_df, participants_df):
    """
    Load transformed match data into PostgreSQL.
    Writes the prepared datasets to 'participants' and 'predictions' tables.

    Args: 
        predictions_df
            - pandas.Dataframe: Predictions data
        participants_df
            - pandas.Dataframe: Participants data 
    
    """
    with engine.begin() as conn:
        conn.execute(sqlalchemy.text("TRUNCATE TABLE predictions, participants"))
    
    print('Loading participants_df')
    participants_df.to_sql(name='participants',
              con= engine,
              if_exists = 'append',
              index= False)
    
    print('Loading predictions_df')
    predictions_df.to_sql(name='predictions',
              con= engine,
              if_exists = 'append',
              index= False)

# Extract
pred_df, teams_df = extract()
print(f'Succesfull extraction')
# Transform
predictions_df, participants_df = transform(pred_df, teams_df)
print(f'Succesfull transformation')
# Load
load(predictions_df, participants_df)
print('Loaded succesfully')