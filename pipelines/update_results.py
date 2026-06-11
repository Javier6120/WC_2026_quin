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

def transform(to_update_list):
    updated_list = []
    token = {'X-Auth-Token':token_1}
    for i in to_update_list:
        try:
            response = requests.get(f"https://api.football-data.org/v4/matches/{i}", headers=token)
            json_data = response.json()
            updated_list.append([i,json_data['score']['winner']])
        except: pass
    print(f"IDs to update: {update_list}")
    return updated_list

def load(updated_list):
    update_q = sqlalchemy.text(''' UPDATE matches 
                                   SET result =:res
                                   WHERE api_match_id = :id''')
    for pair in updated_list:
        with engine.begin() as conn:
            conn.execute(update_q, {'res':pair[1], 'id':pair[0]})
    print(f"Updated: {updated_list}")

update_list = to_update()
updated_list = transform(update_list)
load(updated_list)
