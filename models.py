import os
import datetime
from sqlalchemy import create_engine, DateTime, Integer, String, func
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
import atexit

POSTGRES_USER = os.getenv("POSTGRES_USER", 'postgres')
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", '1234')
POSTGRES_DB = os.getenv("POSTGRES_DB", 'posters')
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

PG_DSN = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

engine = create_engine(PG_DSN)
atexit.register(engine.dispose)
Session = sessionmaker(bind=engine)




class Base(DeclarativeBase):

    @property
    def id_dict(self):
        return {'id': self.id}
    

class Posters(Base):
    __tablename__ = 'posters'
 
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    Title: Mapped[str] = mapped_column(String(72), unique=True, nullable=False)
    Description: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    creating_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    Owner: Mapped[str] = mapped_column(String(72), nullable=False)

    @property
    def dict(self):
        return {
            'id': self.id,
            'Title': self.Title,
            'Description': self.Description,
            'creating_time': self.creating_time.isoformat(),
            'Owner': self.Owner,
        }
    
Base.metadata.create_all(bind=engine)