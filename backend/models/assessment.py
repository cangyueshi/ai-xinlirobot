import enum
from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime, func
from database import Base


class RiskLevel(str, enum.Enum):
    NONE = "none"
    YELLOW = "yellow"
    RED = "red"


class AssignStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"


class Scale(Base):
    __tablename__ = "scales"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    questions_json = Column(Text, nullable=False)
    scoring_rules_json = Column(Text, nullable=False)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    visitor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    scale_id = Column(Integer, ForeignKey("scales.id"), nullable=False)
    answers_json = Column(Text, nullable=False)
    total_score = Column(Integer, nullable=False)
    result_level = Column(Enum(RiskLevel), default=RiskLevel.NONE)
    result_detail = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class ScaleAssignment(Base):
    """咨询师分发量表给来访者的记录"""
    __tablename__ = "scale_assignments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    counselor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    visitor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    scale_id = Column(Integer, ForeignKey("scales.id"), nullable=False)
    status = Column(Enum(AssignStatus), default=AssignStatus.PENDING)
    created_at = Column(DateTime, server_default=func.now())