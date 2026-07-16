from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text

from database import Base


class ImageSource(Base):
    __tablename__ = "image_sources"

    image_id = Column(String(64), primary_key=True)
    source_url = Column(Text, nullable=False)
    content_type = Column(String, nullable=True)
    content_etag = Column(String, nullable=True)
    upstream_etag = Column(String, nullable=True)
    upstream_last_modified = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
    )
