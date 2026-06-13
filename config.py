from dotenv import load_dotenv
import os, json
from pathlib import Path

load_dotenv()

# Database connection info
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_port = os.getenv("DB_PORT")
db_password = os.getenv("DB_PASSWORD")

# API Token / Google Sheets Info
token_1 = os.getenv("API_TOKEN_FOOTBALL")
sheet_id = os.getenv("SHEET_ID")

# Name mappinp dictionary
name_map = json.loads(os.getenv("NAME_MAP"))

# Path Settings
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / 'data'
SQL_DIR = PROJECT_ROOT / 'sql'
CREDENTIALS_DIR = PROJECT_ROOT / 'credentials'