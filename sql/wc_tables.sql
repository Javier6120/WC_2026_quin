DROP TABLE IF EXISTS teams CASCADE;
DROP TABLE IF EXISTS matches CASCADE;
DROP TABLE IF EXISTS participants CASCADE;
DROP TABLE IF EXISTS predictions;

CREATE TABLE teams(
	team_id VARCHAR(5) PRIMARY KEY,
	eng_team VARCHAR(50) NOT NULL,
	spa_team VARCHAR(50) NOT NULL);
	
CREATE TABLE participants(
	participant_id INTEGER PRIMARY KEY ,
	name VARCHAR(50) NOT NULL);

CREATE TABLE matches(
	forms_match_id VARCHAR(4) PRIMARY KEY,
	stage VARCHAR(50) NOT NULL,
	home_team_id VARCHAR(5) NOT NULL,
	away_team_id VARCHAR(5) NOT NULL,
	api_match_id INTEGER UNIQUE NOT NULL,
	date TIMESTAMPTZ NOT NULL,
	result VARCHAR(20),
	FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
	FOREIGN KEY (away_team_id) REFERENCES teams(team_id));

CREATE TABLE predictions(
	participant_id INTEGER NOT NULL,
	forms_match_id VARCHAR(3) NOT NULL,
	eng_pred VARCHAR(50) NOT NULL,
	spa_pred VARCHAR(50) NOT NULL,
	PRIMARY KEY (participant_id, forms_match_id),
	FOREIGN KEY (participant_id) REFERENCES participants(participant_id),
	FOREIGN KEY (forms_match_id) REFERENCES matches(forms_match_id));

	
