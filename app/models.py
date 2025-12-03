from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Operator(Base):
    __tablename__ = "operators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    workload_limit = Column(Integer, default=10)

    # Relationships
    source_configs = relationship("SourceOperatorConfig", back_populates="operator")
    contacts = relationship("Contact", back_populates="operator")

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    # Relationships
    operator_configs = relationship("SourceOperatorConfig", back_populates="source")
    contacts = relationship("Contact", back_populates="source")

class SourceOperatorConfig(Base):
    __tablename__ = "source_operator_configs"

    source_id = Column(Integer, ForeignKey("sources.id"), primary_key=True)
    operator_id = Column(Integer, ForeignKey("operators.id"), primary_key=True)
    weight = Column(Integer, default=1)

    # Relationships
    source = relationship("Source", back_populates="operator_configs")
    operator = relationship("Operator", back_populates="source_configs")

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String, unique=True, index=True) # e.g., email, phone

    # Relationships
    contacts = relationship("Contact", back_populates="lead")

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    source_id = Column(Integer, ForeignKey("sources.id"))
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    lead = relationship("Lead", back_populates="contacts")
    source = relationship("Source", back_populates="contacts")
    operator = relationship("Operator", back_populates="contacts")
