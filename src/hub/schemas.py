from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

class Environment(str, Enum):
    AWS = "AWS"
    AZURE = "Azure"
    GCP = "GCP"
    VMWARE = "VMware"
    ON_PREM = "On-Prem"

class KeyState(str, Enum):
    ENABLED = "Enabled"
    DISABLED = "Disabled"
    PENDING_DELETION = "PendingDeletion"
    UNAVAILABLE = "Unavailable"

class CryptographicKey(BaseModel):
    key_id: str = Field(..., description="Unique identifier (ARN, URL, UUID)")
    name: Optional[str] = Field(None, description="Human-readable name or alias")
    environment: Environment
    key_type: str = Field(..., description="RSA, ECC, AES, etc.")
    algorithm: str = Field(..., description="Specific algorithm and size (e.g., RSA-4096)")
    state: KeyState
    creation_date: Optional[datetime]
    rotation_enabled: bool
    rotation_interval_days: Optional[int]
    last_rotated: Optional[datetime]
    expiry_date: Optional[datetime]
    customer_managed: bool = Field(True, description="True if customer managed, False if provider managed")
    usage: Optional[str] = Field(None, description="Linked resources or services")
    last_accessed: Optional[datetime]

class CertificateStatus(str, Enum):
    VALID = "Valid"
    EXPIRED = "Expired"
    REVOKED = "Revoked"
    UNTRUSTED = "Untrusted Root"

class DigitalCertificate(BaseModel):
    common_name: str
    san_entries: List[str] = []
    serial_number: str
    issuer: str
    signature_algorithm: str
    key_size: int
    valid_from: datetime
    valid_to: datetime
    chain_status: CertificateStatus
    source: str = Field(..., description="Where it was found (e.g., AWS ACM, IIS)")
    issuance_type: str = Field(..., description="ACME, Manual, Auto-Enrollment")
    associated_asset: Optional[str] = Field(None, description="Where it is installed")

class IngestRequest(BaseModel):
    keys: List[CryptographicKey] = []
    certificates: List[DigitalCertificate] = []
