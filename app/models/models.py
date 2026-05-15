from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    subscription_status = Column(String, default="pro") # Default to pro for now
    
    families = relationship("Family", back_populates="owner")

class Family(Base):
    __tablename__ = "families"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    default_country = Column(String, default="CH")
    default_year = Column(Integer, default=2026)
    
    owner = relationship("User", back_populates="families")
    members = relationship("FamilyMember", back_populates="family", cascade="all, delete-orphan")

class FamilyMember(Base):
    __tablename__ = "family_members"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    family_id = Column(Integer, ForeignKey("families.id"))
    country = Column(String)
    subdivision = Column(String, nullable=True)
    vacation_allowance = Column(Float)
    working_days = Column(Integer, default=5) # e.g., 5 days per week
    color = Column(String, default="#3b82f6") # Tailwind blue-500
    
    family = relationship("Family", back_populates="members")
    vacations = relationship("Vacation", back_populates="member", cascade="all, delete-orphan")

class Vacation(Base):
    __tablename__ = "vacations"
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("family_members.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    title = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    business_days_spent = Column(Float)
    
    member = relationship("FamilyMember", back_populates="vacations")
