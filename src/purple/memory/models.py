"""SQLAlchemy ORM models. PostgreSQL + pgvector from day one (no SQLite)."""

from __future__ import annotations

from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from purple.config import settings


class Base(DeclarativeBase):
    pass


class Message(Base):
    """Raw conversation log, so Purple can reload context across restarts."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True)
    role: Mapped[str] = mapped_column(String(16))  # user | assistant | tool | system
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )


class Fact(Base):
    """Durable, semantically-searchable memory ('the user lives in Kolkata')."""

    __tablename__ = "facts"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(String(32), default="fact")
    embedding: Mapped[list[float]] = mapped_column(Vector(settings.embed_dim))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Note(Base):
    """A note the user asked Purple to keep."""

    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )


class Reminder(Base):
    """A reminder / simple calendar entry. due_at is optional (open to-dos allowed)."""

    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    done: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ProfileEntry(Base):
    """Structured profile — one row per key (name, location, work, comms_style, ...).
    Distinct from free-form Facts: these are the canonical 'about you' fields."""

    __tablename__ = "profile"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    value: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Entity(Base):
    """A person / project / place / org the user cares about — so Purple knows who
    'my boss' or 'the Helios project' is. People here also inform VIP / call handling."""

    __tablename__ = "entities"

    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(16), index=True)  # person | project | place | org
    name: Mapped[str] = mapped_column(String(128), index=True)
    relation: Mapped[str] = mapped_column(String(64), default="")  # boss | spouse | colleague...
    aliases: Mapped[str] = mapped_column(Text, default="")  # comma-separated
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SessionSummary(Base):
    """A rolling summary of one conversation (episodic memory) — so Purple recalls 'what
    we did' across restarts and stays coherent in long chats beyond the message window."""

    __tablename__ = "session_summaries"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(settings.embed_dim))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Document(Base):
    """A file Purple has ingested into her knowledge base (RAG)."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(String(512), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(256))
    sha: Mapped[str] = mapped_column(String(64))  # content hash → skip unchanged files
    n_chunks: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Chunk(Base):
    """An embedded passage of a Document — the unit RAG retrieval searches over."""

    __tablename__ = "doc_chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), index=True
    )
    ordinal: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(settings.embed_dim))


class Mission(Base):
    """A long-horizon goal Purple plans + executes over time (M5)."""

    __tablename__ = "missions"

    id: Mapped[int] = mapped_column(primary_key=True)
    goal: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default="planned", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Step(Base):
    """One step of a Mission's plan, executed in order (and persisted so it resumes)."""

    __tablename__ = "mission_steps"

    id: Mapped[int] = mapped_column(primary_key=True)
    mission_id: Mapped[int] = mapped_column(
        ForeignKey("missions.id", ondelete="CASCADE"), index=True
    )
    ordinal: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default="pending")
    result: Mapped[str] = mapped_column(Text, default="")


class AutomationRule(Base):
    """A user-defined automation: 'when an event from <source> matching <keywords> at/above
    <min_priority> arrives, <effect> it (speak / mute / notify)'. Authored from the UI or
    by voice; applied by the trigger engine. Kept simple + flat so the UI can edit it."""

    __tablename__ = "automation_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    keywords: Mapped[str] = mapped_column(Text, default="")  # comma-separated; "" = any
    source: Mapped[str] = mapped_column(String(32), default="")  # watcher source; "" = any
    min_priority: Mapped[str] = mapped_column(String(16), default="normal")
    effect: Mapped[str] = mapped_column(String(16), default="notify")  # speak | mute | notify
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    action: Mapped[str] = mapped_column(String(64), default="")  # optional tool to run
    action_args: Mapped[str] = mapped_column(Text, default="{}")  # JSON args for the tool
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
