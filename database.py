from sqlalchemy import create_engine
from config import db_host, db_name, db_user, db_port, db_password

connection_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(connection_url, pool_pre_ping=True, pool_size=5, max_overflow=10)