from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.conf.config import settings
# SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:567234@195.201.150.230:5433/a_makusheva_fa"
# SQLALCHEMY_DATABASE_URL_FOR_WORK = "sqlite:///contacts.db"

SQLALCHEMY_DATABASE_URL_FOR_WORK = settings.sqlalchemy_database_url

class Connect_db:

  def __init__(self, url: str):
    self.url = url
    #############self.engine = create_engine(url,connect_args={"check_same_thread": False})
    self.engine = create_engine(url)

    self.session = sessionmaker(autocommit=False,
                                autoflush=False,
                                bind=self.engine)

  def __call__(self):
    db = self.session()
    try:
      yield db
    finally:
      db.close()
