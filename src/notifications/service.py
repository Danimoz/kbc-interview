import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.notifications.schema import NotificationCreate
from src.notifications.model import Notifications, DeliveryType
from src.core.worker import send_notification

logger = logging.getLogger(__name__)

async def queue_notification(notification: NotificationCreate, db: AsyncSession):
  '''
  Queue the notification
  '''
  job_id = str(uuid.uuid4())
  try:
    delivery_type_enum = DeliveryType(notification.delivery_type)
  except ValueError:
    raise ValueError(f"Invalid delivery_type: {notification.delivery_type}. Must be one of {[e.value for e in DeliveryType]}")
  
  new_notification = Notifications(
    user_id=notification.user_id,
    message=notification.message,
    delivery_type=delivery_type_enum,
    job_id=job_id
  )
  db.add(new_notification)
  await db.commit()
  await db.refresh(new_notification)

  print(f"Job ID: {job_id}, User ID: {new_notification.user_id}, Notification ID: {new_notification.id}, Message: {new_notification.message}, Delivery Type: {delivery_type_enum.value}")
  # Queue task in Celery
  send_notification.delay(
    job_id,
    new_notification.user_id,
    new_notification.id,
    new_notification.message,
    delivery_type_enum.value
  )

  logger.info(f"Notification queued with job_id: {job_id}")
  return job_id

async def get_notification_by_job_id(db: AsyncSession, job_id: str) -> Notifications:
  """
  Retrieve a notification by its job_id
  """
  query = select(Notifications).where(Notifications.job_id == job_id)
  result = await db.execute(query)
  notification = result.scalar_one_or_none()
  return notification

async def update_notification_status(db: AsyncSession, job_id: str, status: str, error_message: str = None) -> None:
  """
  Update the status of a notification
  """
  notification = await get_notification_by_job_id(db, job_id)
  if notification:
    notification.status = status
    if error_message:
      notification.error_message = error_message
    await db.commit()
    logger.info(f"Updated notification {job_id} status to {status}")


async def get_notifications_by_user(db: AsyncSession, user_id: str):
  """
  Retrieve notifications by user_id
  """
  query = select(Notifications).where(Notifications.user_id == int(user_id)).order_by(
    Notifications.created_at.desc()
  ).limit(10)
  result = await db.execute(query)
  notifications = result.scalars().all()
  return notifications
