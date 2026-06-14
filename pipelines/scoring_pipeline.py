import pandas as pd
from database import engine

def transform():
     q1 = '''  WITH outcomes AS(
                         SELECT forms_match_id, 
                              t.spa_team AS spa_home_team, 
                              tt.spa_team AS spa_away_team, date,
                              CASE WHEN result = 'DRAW' THEN 'Empate'
                                   WHEN result = 'HOME_TEAM' THEN t.spa_team
                                   WHEN result = 'AWAY_TEAM' THEN tt.spa_team
                                   ELSE NULL END AS spa_outcome		
                         FROM matches as m
                         LEFT JOIN teams as t
                         ON m.home_team_id = t.team_id
                         LEFT JOIN teams as tt
                         ON m.away_team_id = tt.team_id),
	          pointed AS (
                         SELECT out.forms_match_id, participant_id, 
                               spa_home_team, spa_away_team,
                               spa_pred, date, spa_outcome,
                               CASE WHEN spa_pred = spa_outcome THEN 1
                                    ELSE 0 END AS points
                         FROM predictions as pred 
                         LEFT JOIN outcomes as out 
                         ON pred.forms_match_id = out.forms_match_id)
	
               SELECT p.forms_match_id, p.participant_id, 
                      name, spa_home_team, spa_away_team, 
                      spa_pred, spa_outcome, points, date
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