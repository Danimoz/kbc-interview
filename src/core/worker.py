import asyncio
import logging
from celery import Celery
from src.core.config import settings
from src.core.db import AsyncSessionLocal
from src.core.rate_limit import rate_limiter
from src.notifications.model import NotificationStatus, DeliveryType
    
celery = Celery(__name__)
celery.conf.broker_url = settings.CELERY_BROKER_URL
celery.conf.result_backend = settings.CELERY_RESULT_BACKEND

logger = logging.getLogger(__name__)

async def get_db_session():
  async with AsyncSessionLocal() as session:
    return session
  

def run_async(coro):
  loop = asyncio.get_event_loop()
  return loop.run_until_complete(coro)


async def update_notification_status_task(job_id: str, status: str, error_message: str = None):
  from src.notifications.service import update_notification_status
  db = await get_db_session()
  try:
    await update_notification_status(db, job_id, status, error_message)
  finally:
    await db.close()

def send_sms_notification():
  try:
    # Your SMS sending logic here
    # ...
    return True  # Success
  except Exception as e:
    print(f"SMS sending failed: {e}")
    return False  # Failure

def send_email_notification():
  try:
    # Your email sending logic here
    # ...
    return True  # Success
  except Exception as e:
    print(f"Email sending failed: {e}")
    return False 

@celery.task(name="send_notification", bind=True)
def send_notification(self, job_id: str, user_id: str, notification_id: str, message: str, delivery_type: str):
  try:
    run_async(update_notification_status_task(job_id, NotificationStatus.PROCESSING))
    delivery_success = False
      
    if delivery_type.lower() == "sms":
      delivery_success = send_sms_notification()
    elif delivery_type.lower() == "email":
      delivery_success = send_email_notification()
    else:
      error_message = f"Invalid delivery type: {delivery_type}"
      run_async(update_notification_status_task(job_id, NotificationStatus.FAILED, error_message))
      return {"status": "failed", "error": error_message}
    
    if delivery_success:
      run_async(update_notification_status_task(job_id, NotificationStatus.DELIVERED))
      run_async(rate_limiter.increment_count(user_id))
      logger.info(f"Successfully delivered notification {job_id}")
      return {"status": "delivered"}
    else:
      error_message = f"Failed to deliver {delivery_type} notification"
      run_async(update_notification_status_task(job_id, NotificationStatus.FAILED, error_message))
      return {"status": "failed", "error": error_message}
  except Exception as e:
    # Update notification status
    print(e)
    run_async(update_notification_status_task(job_id, NotificationStatus.FAILED, str(e)))
    return {"status": "failed", "error": str(e)}