from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_port = os.getenv("DB_PORT")
db_password = os.getenv("DB_PASSWORD")

token_1 = os.getenv("API_TOKEN_FOOTBALL")
sheet_id = os.getenv("SHEET_ID")


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / 'data'
SQL_DIR = PROJECT_ROOT / 'sql'
CREDENTIALS_DIR = PROJECT_ROOT / 'credentials'