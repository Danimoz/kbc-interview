from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.core.db import Base
import enum

class DeliveryType(enum.Enum):
  EMAIL = "email"
  SMS = "sms"

class NotificationStatus(str, enum.Enum):
  PENDING = "pending"
  PROCESSING = "processing"
  DELIVERED = "delivered"
  FAILED = "failed"

class Notifications(Base):
  __tablename__ = "notifications"

  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(Integer, ForeignKey("users.id"))
  message = Column(String, nullable=False)
  job_id = Column(String, unique=True, index=True)
  delivery_type = Column(Enum(DeliveryType), nullable=False)
  status = Column(String, default=NotificationStatus.PENDING.value, index=True)
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

  user = relationship("User", back_populates="notifications")