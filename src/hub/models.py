from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.ext.declarative import declarative_base
from .schemas import Environment, KeyState, CertificateStatus

Base = declarative_base()

class KeyModel(Base):
    __tablename__ = "cryptographic_keys"

    key_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    environment = Column(SQLEnum(Environment))
    key_type = Column(String)
    algorithm = Column(String)
    state = Column(SQLEnum(KeyState))
    creation_date = Column(DateTime, nullable=True)
    rotation_enabled = Column(Boolean)
    rotation_interval_days = Column(Integer, nullable=True)
    last_rotated = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    customer_managed = Column(Boolean)
    usage = Column(String, nullable=True)
    last_accessed = Column(DateTime, nullable=True)

class CertificateModel(Base):
    __tablename__ = "digital_certificates"

    serial_number = Column(String, primary_key=True, index=True)
    common_name = Column(String)
    san_entries = Column(JSON)  # Stored as JSON list
    issuer = Column(String)
    signature_algorithm = Column(String)
    key_size = Column(Integer)
    valid_from = Column(DateTime)
    valid_to = Column(DateTime)
    chain_status = Column(SQLEnum(CertificateStatus))
    source = Column(String)
    issuance_type = Column(String)
    associated_asset = Column(String, nullable=True)
