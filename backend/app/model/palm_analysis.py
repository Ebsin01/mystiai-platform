from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class PalmAnalysis(Base):

    __tablename__ = "palm_analyses"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    image_filename = Column(String)

    palm_width = Column(Float)

    palm_length = Column(Float)

    index_finger_length = Column(Float)

    middle_finger_length = Column(Float)

    landmarks = Column(JSON)

    # -----------------------
    # Palm Results
    # -----------------------

    palm_shape = Column(String)
    palm_shape_confidence = Column(Float)

    heart_line = Column(String)
    heart_line_confidence = Column(Float)

    head_line = Column(String)
    head_line_confidence = Column(Float)

    life_line = Column(String)
    life_line_confidence = Column(Float)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # -----------------------
    # Relationships
    # -----------------------

    user = relationship(
        "User",
        back_populates="analyses"
    )

    report = relationship(
        "PersonalityReport",
        back_populates="analysis",
        uselist=False,
        cascade="all, delete-orphan"
    )