# Desc: Load all models to be used in the application, so Alembic can pick them for migrations
from src.core.db import Base
from src.users.model import User
from src.notifications.model import Notifications