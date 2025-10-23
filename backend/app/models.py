from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, ENUM
import enum
from .database import Base

class Provider(str, enum.Enum):
    youtube = "youtube"
    facebook = "facebook"
    instagram = "instagram"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    provider = Column(ENUM(Provider, name="provider_enum", create_type=True), index=True, nullable=False)
    post_enabled = Column(Boolean, default=True, nullable=False)
    config = Column(JSONB, nullable=False)
    user = relationship("User", back_populates="accounts")
    __table_args__ = (UniqueConstraint("user_id", "provider", name="uq_user_provider"),)
