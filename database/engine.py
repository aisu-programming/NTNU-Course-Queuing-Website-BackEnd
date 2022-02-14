''' Libraries '''
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base



''' Parameters '''
DB_HOST     = os.environ.get("DB_HOST")
DB_USER     = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME     = os.environ.get("DB_NAME")



''' Script '''
DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_engine(DATABASE_URI, convert_unicode=True)
scoped_session_object = scoped_session(sessionmaker(autocommit=False,
                                                    autoflush=False,
                                                    bind=engine))
Base = declarative_base()
Base.query = scoped_session_object.query_property()
db_session = scoped_session_object()



''' Function '''
def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from database.model import Connection, UserObject, CourseObject, OrderObject
    Base.metadata.create_all(bind=engine)