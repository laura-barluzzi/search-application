from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from enerknol import config

engine = create_engine(config.SQLALCHEMY_DATABASE_URI)

db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # noinspection PyUnresolvedReferences
    import enerknol.models
    Base.metadata.create_all(bind=engine)
