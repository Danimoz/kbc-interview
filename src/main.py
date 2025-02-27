from fastapi import FastAPI
import logging

# Routes
from src.users.routes import router as users_router
from src.notifications.routes import router as notifications_router

logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
  title='KBC API',
  description='API for KBC',
  version='1.0.0'
)
app.include_router(users_router)
app.include_router(notifications_router)

@app.get("/")
async def root():
  return {"message": "Hello World"}