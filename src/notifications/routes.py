from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.notifications.schema import NotificationCreate, NotificationResponse, UserNotifications
from src.core.db import get_db
from src.core.rate_limit import rate_limiter
from src.users.utils import JWTBearer
from src.notifications.service import queue_notification, get_notification_by_job_id, get_notifications_by_user

router = APIRouter(
  prefix="/notifications",
  tags=["notifications"],
  dependencies=[Depends(JWTBearer())]
)

@router.post("/send", status_code=status.HTTP_200_OK)
async def send_notification(notification: NotificationCreate, db: AsyncSession = Depends(get_db)):
  if not await rate_limiter.check_limit(notification.user_id):
    raise HTTPException(
      status_code=status.HTTP_429_TOO_MANY_REQUESTS,
      detail="Rate limit exceeded. Try again later."
    )
  
  try:
    # Queue the notification
    job_id = await queue_notification(notification, db)
    return {"message": "Notification queued successfully!", "job_id": job_id}
  except Exception as e:
    print(e)
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to queue notification")
  
@router.get('/status/{job_id}', response_model=NotificationResponse, status_code=status.HTTP_200_OK)
async def get_notification_status(job_id: str, db: AsyncSession = Depends(get_db)):
  # Query the notification status from database
  print(job_id)
  notification = await get_notification_by_job_id(db, job_id)
  if not notification:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
  
  return NotificationResponse(
    job_id=notification.job_id,
    user_id=notification.user_id,
    status=notification.status,
    message=notification.message,
    delivery_type=notification.delivery_type.value,
    id=notification.id 
  )

@router.get("/notifications/user/{user_id}", response_model=UserNotifications)
async def get_user_notifications(user_id: str, db: AsyncSession = Depends(get_db)):
  notifications = await get_notifications_by_user(db, user_id)
  if not notifications:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No notifications found")
  
  return UserNotifications(
    notifications=[
      NotificationResponse(
        job_id=n.job_id,
        status=n.status,
        created_at=n.created_at,
        user_id=n.user_id,
        message=n.message,
        delivery_type=n.delivery_type.value,
        id=n.id,
        updated_at=n.updated_at
    ) for n in notifications
    ]
  )