from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List

from .models import Base, KeyModel, CertificateModel
from .schemas import IngestRequest, CryptographicKey, DigitalCertificate

# Database Setup (SQLite for local dev)
SQLALCHEMY_DATABASE_URL = "sqlite:///./discovery.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cryptographic Discovery Hub")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/ingest", status_code=201)
def ingest_data(payload: IngestRequest, db: Session = Depends(get_db)):
    """
    Ingest discovery data from collectors.
    Upserts keys and certificates based on ID/Serial.
    """
    # Process Keys
    for key in payload.keys:
        db_key = db.query(KeyModel).filter(KeyModel.key_id == key.key_id).first()
        if db_key:
            # Update existing
            for var, value in vars(key).items():
                setattr(db_key, var, value)
        else:
            # Create new
            db_key = KeyModel(**key.dict())
            db.add(db_key)
    
    # Process Certificates
    for cert in payload.certificates:
        db_cert = db.query(CertificateModel).filter(CertificateModel.serial_number == cert.serial_number).first()
        if db_cert:
            # Update existing
            for var, value in vars(cert).items():
                setattr(db_cert, var, value)
        else:
            # Create new
            db_cert = CertificateModel(**cert.dict())
            db.add(db_cert)
            
    db.commit()
    return {"status": "success", "keys_processed": len(payload.keys), "certs_processed": len(payload.certificates)}

@app.get("/keys", response_model=List[CryptographicKey])
def get_keys(db: Session = Depends(get_db)):
    return db.query(KeyModel).all()

@app.get("/certificates", response_model=List[DigitalCertificate])
def get_certificates(db: Session = Depends(get_db)):
    return db.query(CertificateModel).all()
