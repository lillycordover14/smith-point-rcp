from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, SmallInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Person(Base):
    __tablename__ = "persons"

    id           = Column(Integer, primary_key=True, index=True)
    full_name    = Column(String, nullable=False, index=True)
    first_name   = Column(String)
    last_name    = Column(String)
    email        = Column(String, unique=True, nullable=True)
    linkedin_url = Column(String, unique=True, nullable=True)
    location     = Column(String)
    bio          = Column(Text)
    photo_url    = Column(String)
    current_title   = Column(String)
    current_company = Column(String)
    is_internal  = Column(Boolean, default=False)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    updated_at   = Column(DateTime(timezone=True), onupdate=func.now())

    roles        = relationship("Role", back_populates="person", cascade="all, delete-orphan")
    education    = relationship("Education", back_populates="person", cascade="all, delete-orphan")
    interactions_as_internal = relationship("Interaction", foreign_keys="Interaction.internal_person_id", back_populates="internal_person")
    interactions_as_external = relationship("Interaction", foreign_keys="Interaction.external_person_id", back_populates="external_person")


class Organization(Base):
    __tablename__ = "organizations"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String, nullable=False, index=True)
    linkedin_slug = Column(String, unique=True, nullable=True, index=True)
    domain       = Column(String, unique=True, nullable=True)
    hq_location  = Column(String)
    industry     = Column(String)
    is_portfolio = Column(Boolean, default=False)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    roles        = relationship("Role", back_populates="org")


class Role(Base):
    __tablename__ = "roles"

    id         = Column(Integer, primary_key=True, index=True)
    person_id  = Column(Integer, ForeignKey("persons.id"), nullable=False, index=True)
    org_id     = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    title      = Column(String)
    department = Column(String)
    start_year = Column(SmallInteger)
    end_year   = Column(SmallInteger, nullable=True)   # NULL = current
    is_board   = Column(Boolean, default=False)
    is_current = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    person     = relationship("Person", back_populates="roles")
    org        = relationship("Organization", back_populates="roles")


class Education(Base):
    __tablename__ = "education"

    id          = Column(Integer, primary_key=True, index=True)
    person_id   = Column(Integer, ForeignKey("persons.id"), nullable=False, index=True)
    institution = Column(String, nullable=False)
    degree      = Column(String)
    field       = Column(String)
    start_year  = Column(SmallInteger)
    end_year    = Column(SmallInteger)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    person      = relationship("Person", back_populates="education")


class Interaction(Base):
    __tablename__ = "interactions"

    id                 = Column(Integer, primary_key=True, index=True)
    internal_person_id = Column(Integer, ForeignKey("persons.id"), nullable=False)
    external_person_id = Column(Integer, ForeignKey("persons.id"), nullable=False)
    interaction_type   = Column(String)   # email, meeting, call, event, linkedin
    occurred_at        = Column(DateTime(timezone=True), nullable=False)
    notes              = Column(Text)
    sentiment          = Column(SmallInteger, default=0)  # -2 to 2
    created_at         = Column(DateTime(timezone=True), server_default=func.now())

    internal_person = relationship("Person", foreign_keys=[internal_person_id], back_populates="interactions_as_internal")
    external_person = relationship("Person", foreign_keys=[external_person_id], back_populates="interactions_as_external")
