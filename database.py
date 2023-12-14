from urllib.parse import quote
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import configparser

DB = 'mysql'
DB_CONNECTOR = 'mysqlconnector'

CFG = configparser.RawConfigParser()
CFG.read('db_config.ini')

database_hostname = CFG['db_credentials']['database_hostname']
database_port = CFG['db_credentials']['database_port']
database_password = CFG['db_credentials']['database_password']
database_name = CFG['db_credentials']['database_name']
database_username = CFG['db_credentials']['database_username']

SQLALCHEMY_DATABASE_URL = f'{ DB }+{ DB_CONNECTOR }://{database_username}:{quote(database_password)}@{database_hostname}:{database_port}/{database_name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

session = SessionLocal()

@contextmanager
def get_session():
    s = SessionLocal()
    try:
        yield s
        # s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
        # db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
