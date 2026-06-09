import pandas as pd, sqlalchemy 
from database import engine

def transform():
     q1 = '''  WITH outcomes AS(
               SELECT forms_match_id, home_team, away_team,
                     CASE WHEN result = 'DRAW' THEN 'Draw'
                     WHEN result = 'HOME_TEAM' THEN home_team
                     WHEN result = 'AWAY_TEAM' THEN away_team
                     ELSE NULL END AS outcome
               FROM matches),

               pointed AS(
                    SELECT participant_id, 
                           home_team || ' vs ' || away_team AS match_name,
                           eng_pred,
                           outcome,
                           CASE WHEN eng_pred = outcome THEN 1
                                ELSE 0 END AS points
                    FROM predictions as pred 
                    LEFT JOIN outcomes as out 
                    ON pred.forms_match_id = out.forms_match_id)

               SELECT p.participant_id, name, match_name, eng_pred, outcome, points
               FROM pointed as p
               LEFT JOIN participants AS part 
               ON p.participant_id = part.participant_id
               ORDER BY p.participant_id ASC;'''
     
     scored_df = pd.read_sql(q1,engine)
     leaderboard_df = scored_df.groupby(['participant_id','name'],as_index=False).agg(total_points=('points','sum'))
     leaderboard_df = leaderboard_df.sort_values('total_points',ascending=False).drop(columns=['participant_id'])
     return scored_df, leaderboard_df

def load(scored, lb):
    lb.to_sql(name='leaderboard', con= engine, if_exists = 'replace', index= False)
    scored.to_sql(name='scored', con= engine, if_exists = 'replace', index= False)

pd.set_option('display.max_rows',None)
scored_df,LB_df = transform()
load(scored_df,LB_df)