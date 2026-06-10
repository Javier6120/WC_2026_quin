from sqlalchemy import create_engine
from config import db_host, db_name, db_user, db_port, db_password, neon_host, neon_user, neon_port, neon_pw

connection_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(connection_url, pool_pre_ping=True, pool_size=5, max_overflow=10)

neon_url = f'postgresql://{neon_user}:{neon_pw}@{neon_host}:{neon_port}/neondb?sslmode=require'
neon_engine = create_engine(neon_url)