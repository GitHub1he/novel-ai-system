from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    avatar = Column(String, nullable=True)

    # 用户偏好
    preferred_genre = Column(String, nullable=True)  # 偏好创作类型

    # 权限
    is_admin = Column(Integer, default=0)  # 0: 普通用户, 1: 管理员
    is_active = Column(Integer, default=1)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
