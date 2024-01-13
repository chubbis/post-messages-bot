from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import config

Base = declarative_base()
engine = create_engine(config.PG_DSN)

# # # sync connection
db_session = sessionmaker(bind=engine)()
