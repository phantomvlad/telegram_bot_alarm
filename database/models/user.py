from .base import Base
from sqlalchemy.orm import relationship

from sqlalchemy import Column, Integer, BigInteger, String

class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False, unique=True)
    routes = relationship('Route', backref='user')