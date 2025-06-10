from datetime import datetime
from typing import Optional
from uuid import UUID as pyUUID

from infrastructure.enums.category import Category
from infrastructure.enums.order_status import OrderStatus
from infrastructure.enums.payout_time import PayoutTime
from infrastructure.enums.product_status import ProductStatus
from infrastructure.enums.push_status import PushStatus
from infrastructure.enums.user_role import UserRole
from sqlalchemy import DateTime, ForeignKey, UUID, BigInteger, Enum, Text, Boolean
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship

from infrastructure.enums.story_status import StoryStatus
from infrastructure.enums.user_status import UserStatus

Base = declarative_base()


class AbstractBase(Base):
    __abstract__ = True

    id: Mapped[pyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)


class User(AbstractBase):
    __tablename__ = "managers"
    telegram_id: Mapped[Optional[int]] = mapped_column(BigInteger, unique=True)
    nickname: Mapped[Optional[str]]
    status: Mapped[UserStatus] = mapped_column(default=UserStatus.USER)
    session_string: Mapped[str] = mapped_column(Text, nullable=False)
    stories = relationship("Story", back_populates="manager")


class Story(AbstractBase):
    __tablename__ = "stories"
    manager_id: Mapped[pyUUID] = mapped_column(UUID(as_uuid=True), ForeignKey("managers.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    scheduled_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[StoryStatus] = mapped_column(Enum(StoryStatus), default=StoryStatus.pending)
    manager = relationship("Manager", back_populates="stories")


class Service(AbstractBase):
    __tablename__ = 'services'
    name: Mapped[str]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
