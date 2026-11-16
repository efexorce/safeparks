import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SAEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.db.session import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"
    FIELD_OFFICER = "field_officer"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(500), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(SAEnum(UserRole), default=UserRole.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    last_login_at = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    notification_preferences = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


from sqlalchemy import Integer
