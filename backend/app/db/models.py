import uuid
from datetime import datetime, date, time
from sqlalchemy import (
    Column, String, Boolean, Integer, Date, Time, Text, DateTime,
    ForeignKey, BigInteger, UniqueConstraint, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


def new_uuid():
    return str(uuid.uuid4())


class Kindergarten(Base):
    __tablename__ = "kindergartens"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    name = Column(String(255), nullable=False)
    city = Column(String(100))
    address = Column(Text)
    phone = Column(String(30))
    created_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)

    groups = relationship("Group", back_populates="kindergarten")
    users = relationship("User", back_populates="kindergarten")
    children = relationship("Child", back_populates="kindergarten")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    kindergarten_id = Column(UUID(as_uuid=False), ForeignKey("kindergartens.id"))
    role = Column(String(20), nullable=False)  # admin | teacher | parent | superadmin
    full_name = Column(String(255), nullable=False)
    phone = Column(String(30))
    email = Column(String(255), unique=True)
    password_hash = Column(String(255))
    telegram_id = Column(BigInteger, unique=True)
    telegram_username = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    kindergarten = relationship("Kindergarten", back_populates="users")
    taught_groups = relationship("Group", back_populates="teacher", foreign_keys="Group.teacher_id")
    attendance_marked = relationship("Attendance", back_populates="marked_by_user")
    parent_children = relationship("ParentChild", back_populates="parent")
    posts = relationship("Post", back_populates="author")


class Group(Base):
    __tablename__ = "groups"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    kindergarten_id = Column(UUID(as_uuid=False), ForeignKey("kindergartens.id"))
    name = Column(String(100), nullable=False)
    age_from = Column(Integer)
    age_to = Column(Integer)
    teacher_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())

    kindergarten = relationship("Kindergarten", back_populates="groups")
    teacher = relationship("User", back_populates="taught_groups", foreign_keys=[teacher_id])
    children = relationship("Child", back_populates="group")
    schedule_items = relationship("Schedule", back_populates="group")


class Child(Base):
    __tablename__ = "children"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    kindergarten_id = Column(UUID(as_uuid=False), ForeignKey("kindergartens.id"))
    group_id = Column(UUID(as_uuid=False), ForeignKey("groups.id"))
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    birth_date = Column(Date, nullable=False)
    gender = Column(String(10))  # M | F
    photo_url = Column(Text)
    allergies = Column(Text)
    medical_notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)

    kindergarten = relationship("Kindergarten", back_populates="children")
    group = relationship("Group", back_populates="children")
    attendance = relationship("Attendance", back_populates="child")
    parent_links = relationship("ParentChild", back_populates="child")
    medical_records = relationship("MedicalRecord", back_populates="child")
    documents = relationship("Document", back_populates="child")


class ParentChild(Base):
    __tablename__ = "parent_child"

    parent_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), primary_key=True)
    child_id = Column(UUID(as_uuid=False), ForeignKey("children.id"), primary_key=True)
    relation = Column(String(30))  # mother | father | guardian

    parent = relationship("User", back_populates="parent_children")
    child = relationship("Child", back_populates="parent_links")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    child_id = Column(UUID(as_uuid=False), ForeignKey("children.id"))
    date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False)  # present | absent_sick | absent_vacation | absent_other
    note = Column(Text)
    marked_by = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    marked_at = Column(DateTime, default=func.now())

    __table_args__ = (UniqueConstraint("child_id", "date", name="uq_attendance_child_date"),)

    child = relationship("Child", back_populates="attendance")
    marked_by_user = relationship("User", back_populates="attendance_marked")


class Schedule(Base):
    __tablename__ = "schedule"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    group_id = Column(UUID(as_uuid=False), ForeignKey("groups.id"))
    day_of_week = Column(Integer, nullable=False)  # 1=Mon ... 5=Fri
    time_start = Column(Time, nullable=False)
    time_end = Column(Time, nullable=False)
    subject = Column(String(100), nullable=False)
    teacher_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    room = Column(String(50))

    group = relationship("Group", back_populates="schedule_items")


class Menu(Base):
    __tablename__ = "menu"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    kg_id = Column(UUID(as_uuid=False), ForeignKey("kindergartens.id"))
    date = Column(Date, nullable=False)
    meal_type = Column(String(20), nullable=False)  # breakfast | lunch | snack | dinner
    description = Column(Text, nullable=False)
    calories = Column(Integer)


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    kg_id = Column(UUID(as_uuid=False), ForeignKey("kindergartens.id"))
    group_id = Column(UUID(as_uuid=False), ForeignKey("groups.id"))
    author_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    type = Column(String(20), nullable=False)  # news | announcement | photo
    title = Column(String(255))
    content = Column(Text)
    media_urls = Column(ARRAY(Text))
    created_at = Column(DateTime, default=func.now())
    is_sent = Column(Boolean, default=False)

    author = relationship("User", back_populates="posts")


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    child_id = Column(UUID(as_uuid=False), ForeignKey("children.id"))
    record_type = Column(String(30))  # vaccination | illness | checkup
    title = Column(String(255))
    description = Column(Text)
    date = Column(Date)
    next_date = Column(Date)
    created_at = Column(DateTime, default=func.now())

    child = relationship("Child", back_populates="medical_records")


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    child_id = Column(UUID(as_uuid=False), ForeignKey("children.id"))
    kg_id = Column(UUID(as_uuid=False), ForeignKey("kindergartens.id"))
    type = Column(String(50))  # contract | consent | medical_cert
    title = Column(String(255))
    file_url = Column(Text)
    created_at = Column(DateTime, default=func.now())

    child = relationship("Child", back_populates="documents")


class TelegramSession(Base):
    __tablename__ = "telegram_sessions"

    telegram_id = Column(BigInteger, primary_key=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    state = Column(String(100))
    state_data = Column(JSONB)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class InviteCode(Base):
    __tablename__ = "invite_codes"

    id = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    code = Column(String(10), nullable=False, unique=True)
    kg_id = Column(UUID(as_uuid=False), ForeignKey("kindergartens.id"))
    role = Column(String(20), nullable=False)  # teacher | parent
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))  # pre-created user, optional
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
