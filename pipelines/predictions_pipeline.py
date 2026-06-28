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
from config import sheet_id, sheet_ko, CREDENTIALS_DIR, name_map

def extract(): 
    """
    Extract predictions data from Google Sheets API. 

    Returns: 
        group_predictions_DF, teams_df, ko_preds_list
            - pandas.DataFrame: Group matches predictions (Sheets Data)
            - pandas.DataFrame: Teams table
            - list[pandas.DataFrame]: List of predictions per elimination stage
    
    """
    # Google Services Persmissions + Authentication
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_file(CREDENTIALS_DIR/'credentials.json', scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds)

    # API Request (Group Stage)
    form_entries = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="Respuestas de formulario 1").execute()
    group_predictions_DF = pd.DataFrame(form_entries['values'][1:], columns=form_entries['values'][0])

    # API Request (Knockout Predictions)
    ko_preds_list = []
    for page in ['LAST_32','LAST_16','QFS','SFs','Final_TP']:
        form_entries = service.spreadsheets().values().get(spreadsheetId=sheet_ko, range=page).execute()
        phase_preds = pd.DataFrame(form_entries['values'][1:], columns=form_entries['values'][0])
        phase_preds.drop(columns=['Marca temporal'],inplace=True)
        ko_preds_list.append(phase_preds)

    # Read teams table from PostgreSQL
    teams_df = pd.read_sql("SELECT * FROM teams",engine)
    return group_predictions_DF, teams_df, ko_preds_list


def transform(group_preds_df, teams_df, ko_preds_list):
    """
    Prepares dataset for loading into PostgreSQL.
    Joins all predictions into one dataset.
    Cleans data and converts wide format to long format.  
    Generates dataframe with participants data.

    Args:
        group_preds_df
            - pandas.Dataframe: Group predictions G-Sheets Data
        teams_df
            - pandas.Dataframe: Teams table
        ko_preds_list
            - list[pandas.DataFrame]: List of dataframes, each for every elimination stage

    Returns: 
        predictions_df
            - pandas.Dataframe: Predictions Data
        participants_df
            - pandas.Dataframe: Participants Data
        
    """
    # Name standardization in group predictions DF
    name_map_dict = name_map
    group_preds_df['Nombre'] = group_preds_df['Nombre'].str.strip()
    group_preds_df['Nombre'] = group_preds_df['Nombre'].str.title()
    group_preds_df['Nombre'] = group_preds_df['Nombre'].replace(name_map_dict)
    group_preds_df.drop(columns=['Marca temporal'],inplace=True)

    # Clean incorrect country name 
    group_preds_df = group_preds_df.replace('Bosnia Herzegobina','Bosnia Herzegovina')

    # Merge all predictions into one dataframe
    full_predictions_df = group_preds_df
    for data_frame in ko_preds_list:
        full_predictions_df = pd.merge(full_predictions_df,data_frame,left_on='Nombre',right_on='Nombre',how='left')
    
    # Melt columns into rows 
    full_predictions_df = full_predictions_df.melt(id_vars='Nombre',
                                         var_name='forms_match_id',
                                         value_name='pred')
    full_predictions_df.rename(columns={'Nombre':'participant'}, inplace=True)
    
    # Add team names in english 
    full_predictions_df = pd.merge(full_predictions_df,teams_df,
                              left_on='pred',
                              right_on='spa_team',
                              how='left').drop(columns=['spa_team','team_id'])
    
    # Fill Draws 
    mask = full_predictions_df['pred']=='Empate'
    full_predictions_df.loc[mask,'eng_team'] = full_predictions_df.loc[mask,'eng_team'].fillna('Draw')

    # Fill no submitted predictions
    full_predictions_df = full_predictions_df.fillna('Pendiente')
    full_predictions_df.rename(columns={'eng_team':'eng_pred', 'pred':'spa_pred'}, inplace=True)

    # Assign id to each participant
    participants_df = pd.DataFrame(full_predictions_df['participant'].unique(),columns=['name'])
    participants_df.reset_index(names='participant_id',inplace=True)

    full_predictions_df = pd.merge(participants_df, full_predictions_df,
                              left_on='name',
                              right_on='participant',
                              how='right').drop(columns=['participant','name'])

    # Exlude no registered matches
    registered_matches = pd.read_sql("SELECT forms_match_id FROM matches",engine)['forms_match_id']
    predictions_df = full_predictions_df[full_predictions_df['forms_match_id'].isin(registered_matches)]

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
group_preds_df, teams_df, ko_preds = extract()
print(f'Succesfull extraction')
# Transform
predictions_df, participants_df = transform(group_preds_df, teams_df, ko_preds)
print(f'Succesfull transformation')
# Load
load(predictions_df, participants_df)
print('Loaded succesfully')