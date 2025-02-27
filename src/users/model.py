from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.core.db import Base

class User(Base):
  __tablename__ = "users"

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, nullable=False)
  email = Column(String, unique=True, index=True, nullable=False)
  password = Column(String, nullable=False)

  notifications = relationship("Notifications", back_populates="user")