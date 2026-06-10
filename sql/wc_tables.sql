DROP TABLE IF EXISTS participants CASCADE;
CREATE TABLE participants(
	participant_id INTEGER PRIMARY KEY ,
	name VARCHAR(50) NOT NULL);

DROP TABLE IF EXISTS matches CASCADE;
CREATE TABLE matches(
	forms_match_id VARCHAR(3) PRIMARY KEY,
	home_team VARCHAR(50) NOT NULL,
	away_team VARCHAR(50) NOT NULL,
	api_match_id INTEGER UNIQUE NOT NULL,
	date TIMESTAMPTZ NOT NULL, 
	result VARCHAR(20));

DROP TABLE IF EXISTS predictions;
CREATE TABLE predictions(
	participant_id INTEGER NOT NULL,
	forms_match_id VARCHAR(3) NOT NULL,
	eng_pred VARCHAR(50) NOT NULL,
	spa_pred VARCHAR(50) NOT NULL,
	PRIMARY KEY (participant_id, forms_match_id),
	FOREIGN KEY (participant_id) REFERENCES participants(participant_id),
	FOREIGN KEY (forms_match_id) REFERENCES matches(forms_match_id));