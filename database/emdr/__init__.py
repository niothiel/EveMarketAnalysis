import config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(config.DB_CONNECTIONSTRING, echo=config.debug)
Base = declarative_base()

# TODO: Look into using a scoped session for this.
Session = sessionmaker(bind=engine)
session = Session()

# Import the models
from history import History
from order import Order

# Create the database if it doesn't exist yet.
Base.metadata.create_all(engine)

