from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import pandas as pd, sqlalchemy 
from database import engine
from config import sheet_id, DATA_DIR, CREDENTIALS_DIR, name_map

def extract(): 
    # Google Services Presmissions
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

    # Authentication
    creds = Credentials.from_service_account_file(CREDENTIALS_DIR/'credentials.json', scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds)

    # API Request
    form_entries = service.spreadsheets().values().get(spreadsheetId=sheet_id, 
                                                       range="Respuestas de formulario 1").execute()
    predictions_DF = pd.DataFrame(form_entries['values'][1:], columns=form_entries['values'][0])

    # Read CSV with team names translations (eng-spa)
    translation_df = pd.read_csv(DATA_DIR/'wc_teams.csv')
    return predictions_DF,translation_df


def transform(predictions_df, teams_df):
    name_map_dict = name_map
    # Cleaning
    predictions_df['Nombre'] = predictions_df['Nombre'].str.strip()
    predictions_df['Nombre'] = predictions_df['Nombre'].str.title()
    predictions_df['Nombre'] = predictions_df['Nombre'].replace(name_map_dict)
    predictions_df.rename(columns={'Nombre':'participant'}, inplace=True)
    predictions_df.drop(columns=['Marca temporal'],inplace=True)

    # Melt columns to forms_match_id
    predictions_df = predictions_df.melt(id_vars='participant',
                                         var_name='forms_match_id',
                                         value_name='pred')
    predictions_df = pd.merge(predictions_df,teams_df,
                              left_on='pred',
                              right_on='spa_team',
                              how='left').drop(columns=['spa_team'])
   
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
    with engine.begin() as conn:
        conn.execute(sqlalchemy.text("TRUNCATE TABLE predictions, participants"))
    participants_df.to_sql(name='participants',
              con= engine,
              if_exists = 'append',
              index= False)
    predictions_df.to_sql(name='predictions',
              con= engine,
              if_exists = 'append',
              index= False)

pred_df, teams_df = extract()
predictions_df, participants_df = transform(pred_df, teams_df)
load(predictions_df, participants_df)