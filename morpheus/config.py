import os
from dotenv import load_dotenv

load_dotenv()

class Config():
    # Flask settings
    FLASK_ENV: str=os.environ.get("FLASK_ENV", 'production')
    PORT: int=os.environ.get("PORT", 8000)
    HOST: str=os.environ.get("HOST", 'localhost')
    FLASK_DEBUG: bool= os.environ.get("FLASK_DEBUG", False)

    # SQLAlchemy settings
    SQLALCHEMY_DATABASE_TYPE: str='sqlite:///'
    DATABASE_PATH: str=os.environ.get("DATABASE_PATH", ':memory:')
    SQLALCHEMY_TRACK_MODIFICATIONS: bool=os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    # Analysis
    TACOCO_HOME: str= os.environ.get("TACOCO_HOME", None)
    PARSER_HOME: str= os.environ.get("PARSER_HOME", None)