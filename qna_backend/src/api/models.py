from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from sqlalchemy import Integer, String, DateTime, ForeignKey, Text, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.database import Base


class User(Base):
    """User account model."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    questions: Mapped[List["Question"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    answers: Mapped[List["Answer"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Question(Base):
    """Question model linked to user."""
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["User"] = relationship(back_populates="questions")

    answers: Mapped[List["Answer"]] = relationship(back_populates="question", cascade="all, delete-orphan")


class Answer(Base):
    """Answer model, can be AI generated (user_id nullable)."""
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0", nullable=False)

    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False, index=True)
    question: Mapped["Question"] = relationship(back_populates="answers")

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    user: Mapped[Optional["User"]] = relationship(back_populates="answers")
