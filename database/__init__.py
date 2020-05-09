from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from settings import DATABASE_PATH
from handlers.config_handler import CONFIG

SQLITE_ABS_PATH_BASE_URI = "sqlite:////"
config = CONFIG

if 'custom_db_path' in config:
    db_path = config["custom_db_path"]
else:
    db_path = '{}{}'.format(SQLITE_ABS_PATH_BASE_URI, DATABASE_PATH)

# Create a database engine.
engine = create_engine(db_path)

# Create a configured "Session" class.
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Returns a new base class from which all mapped classes should inherit.
Base = declarative_base()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from database.models.channel import Channel
    from database.models.video import Video
    Base.metadata.create_all(bind=engine)

