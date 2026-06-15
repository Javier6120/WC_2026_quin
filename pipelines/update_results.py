"""
update_scores.py

Selects past matches without registered result 
and request results from Football API.

Filters finished matches and update data in matches table.

Source: 
    Football API 

Target Tables:
    matches (Neon DB)

"""
import pandas as pd 
import sqlalchemy, requests
from database import engine
from config import token_1

def to_update():
     q1 = '''  SELECT api_match_id AS ids
               FROM matches 
               WHERE date<=CURRENT_TIMESTAMP 
                     AND result IS NULL;'''
     to_update = pd.read_sql(q1,engine)
     return(to_update['ids'].tolist())

def extract(to_update_list):
    """
    Extracts data from each match in list 
    and appends succesfull requests with finished status. 

    Args: 
        to_update_list
            - List: API IDs from past matches without registered result.

    Returns:
        updated_list
            - List[List]: List of IDs and result pairs.
    
    """
    updated_list = []
    token = {'X-Auth-Token':token_1}
    for i in to_update_list:
        try:
            response = requests.get(f"https://api.football-data.org/v4/matches/{i}", headers=token)
            json_data = response.json()
            if json_data['status']== 'FINISHED':
                updated_list.append([i,json_data['score']['winner']])
        except: pass
    print(f"IDs to update: {update_list}")
    return updated_list

def load(updated_list):
    """
    LoaUpdates matches table with obtained results in list. 

    Args: 
        updated_list
            - List[List]: List of [ID,result].
    
    """
    update_q = sqlalchemy.text(''' UPDATE matches 
                                   SET result =:res
                                   WHERE api_match_id = :id''')
    for pair in updated_list:
        with engine.begin() as conn:
            conn.execute(update_q, {'res':pair[1], 'id':pair[0]})
    print(f"Updated: {updated_list}")

# Requiered data
update_list = to_update()
# Extract 
updated_list = extract(update_list)
# Load/Update
load(updated_list)
