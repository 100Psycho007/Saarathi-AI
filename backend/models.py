from sqlalchemy import Column, Integer, String, Text, DateTime
from db import Base


class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    short_description = Column(Text, nullable=False)
    full_description = Column(Text, nullable=True)
    category = Column(String, nullable=True)  # e.g., "student", "farmer", "women", "elderly"
    state = Column(String, nullable=False)  # e.g., "Karnataka", "Central"
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)
    min_income = Column(Integer, nullable=True)
    max_income = Column(Integer, nullable=True)
    occupation = Column(String, nullable=True)  # e.g., "farmer", "student"
    gender = Column(String, nullable=True)  # e.g., "Female", "Male", "Any"
    caste = Column(String, nullable=True)  # e.g., "SC", "ST", "OBC", "General", "Any"
    disability = Column(String, nullable=True)  # e.g., "Yes", "No", "Any"
    official_link = Column(String, nullable=True)
    application_process = Column(Text, nullable=True)
    
    # Ingestion tracking fields
    source = Column(String, nullable=True)  # e.g. "myscheme", "data_gov"
    source_scheme_id = Column(String, nullable=True, index=True)  # External ID from source
    last_synced_at = Column(DateTime, nullable=True)  # Last sync timestamp


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    state = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=True)
    occupation = Column(String, nullable=True)
    annual_income = Column(Integer, nullable=True)
    caste = Column(String, nullable=True)  # e.g., "SC", "ST", "OBC", "General"
    disability = Column(String, nullable=True)  # e.g., "Yes", "No"


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=True)
