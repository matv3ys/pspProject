from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

async_engine = create_engine(
    url=settings.GET_DATABASE_URL_psycopg,
    echo=False,
)

session_factory = sessionmaker(async_engine)