from .base import Base

from sqlalchemy import Column, Integer, String, Enum, Time, Date, ForeignKey, BigInteger, Float
from sqlalchemy.dialects.postgresql import ARRAY

class Route(Base):
	__tablename__ = "routes"
	id = Column(BigInteger, autoincrement=True, primary_key=True)
	title = Column(String(200), nullable=False)
	start = Column(ARRAY(Float), nullable=False)
	stop = Column(ARRAY(Float), nullable=False)
	time_end = Column(Time, nullable=False)
	time_other = Column(Time, nullable=False, default=0)
	days_date = Column(ARRAY(Date), default=[])
	days_week = Column(ARRAY(Integer), default=[])
	timezone = Column(String, nullable=False)
	time_average = Column(Integer, nullable=False)
	user_id = Column(BigInteger, ForeignKey('users.user_id'), primary_key=True)