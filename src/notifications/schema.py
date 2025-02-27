from pydantic import BaseModel
from typing import List

class NotificationCreate(BaseModel):
  message: str
  user_id: int
  delivery_type: str


class NotificationResponse(BaseModel):
  id: int
  message: str
  user_id: int
  delivery_type: str
  status: str
  job_id: str

  class Config:
    from_attributes = True


class UserNotifications(BaseModel):
  notifications: List[NotificationResponse]