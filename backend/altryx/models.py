import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from altryx.database import Base


def gen_id() -> str:
    return uuid.uuid4().hex[:12]


class Workflow(Base):
    __tablename__ = "workflows"

    id: Mapped[str] = mapped_column(String(12), primary_key=True, default=gen_id)
    name: Mapped[str] = mapped_column(String(255), default="Untitled Workflow")
    definition: Mapped[str] = mapped_column(Text, default="{}")  # JSON blob: {nodes, edges}
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class Execution(Base):
    __tablename__ = "executions"

    id: Mapped[str] = mapped_column(String(12), primary_key=True, default=gen_id)
    workflow_id: Mapped[str] = mapped_column(String(12))
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending|running|completed|failed
    result: Mapped[str] = mapped_column(Text, default="{}")  # JSON blob with per-node results
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id: Mapped[str] = mapped_column(String(12), primary_key=True, default=gen_id)
    filename: Mapped[str] = mapped_column(String(255))
    original_name: Mapped[str] = mapped_column(String(255))
    file_format: Mapped[str] = mapped_column(String(10))  # csv, xlsx, json
    size_bytes: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
