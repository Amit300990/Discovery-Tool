import boto3
import datetime
from typing import List
from src.hub.schemas import CryptographicKey, DigitalCertificate, Environment, KeyState, CertificateStatus, IngestRequest

class AWSCollector:
    def __init__(self, region_name: str = "us-east-1"):
        self.region = region_name
        self.kms_client = boto3.client("kms", region_name=region_name)
        self.acm_client = boto3.client("acm", region_name=region_name)

    def collect_keys(self) -> List[CryptographicKey]:
        keys = []
        paginator = self.kms_client.get_paginator("list_keys")
        
        for page in paginator.paginate():
            for k in page["Keys"]:
                try:
                    meta = self.kms_client.describe_key(KeyId=k["KeyId"])["KeyMetadata"]
                    
                    # Determine State
                    state_map = {
                        "Enabled": KeyState.ENABLED,
                        "Disabled": KeyState.DISABLED,
                        "PendingDeletion": KeyState.PENDING_DELETION,
                        "Unavailable": KeyState.UNAVAILABLE
                    }
                    
                    # Check rotation
                    rotation = False
                    try:
                        rot_status = self.kms_client.get_key_rotation_status(KeyId=k["KeyId"])
                        rotation = rot_status["KeyRotationEnabled"]
                    except:
                        pass # Managed keys might not allow this call

                    keys.append(CryptographicKey(
                        key_id=meta["Arn"],
                        name=meta.get("Description", k["KeyId"]),
                        environment=Environment.AWS,
                        key_type=meta.get("KeyUsage", "UNKNOWN"),
                        algorithm=f"{meta.get('CustomerMasterKeySpec', 'SYMMETRIC_DEFAULT')}",
                        state=state_map.get(meta["KeyState"], KeyState.UNAVAILABLE),
                        creation_date=meta["CreationDate"],
                        rotation_enabled=rotation,
                        rotation_interval_days=365 if rotation else None, # AWS default is approx 1 year
                        customer_managed=meta["KeyManager"] == "CUSTOMER",
                        usage=meta.get("KeyUsage", "ENCRYPT_DECRYPT"),
                        last_accessed=None # Requires CloudTrail lookup, skipping for basic collector
                    ))
                except Exception as e:
                    print(f"Error processing key {k['KeyId']}: {e}")
        return keys

    def collect_certificates(self) -> List[DigitalCertificate]:
        certs = []
        paginator = self.acm_client.get_paginator("list_certificates")
        
        for page in paginator.paginate():
            for c in page["CertificateSummaryList"]:
                try:
                    details = self.acm_client.describe_certificate(CertificateArn=c["CertificateArn"])["Certificate"]
                    
                    # Determine Status
                    status_map = {
                        "ISSUED": CertificateStatus.VALID,
                        "EXPIRED": CertificateStatus.EXPIRED,
                        "REVOKED": CertificateStatus.REVOKED,
                        "VALIDATION_TIMED_OUT": CertificateStatus.UNTRUSTED
                    }

                    certs.append(DigitalCertificate(
                        common_name=details["DomainName"],
                        san_entries=details.get("SubjectAlternativeNames", []),
                        serial_number=details.get("Serial", c["CertificateArn"]), # ACM doesn't always expose serial in summary
                        issuer=details.get("Issuer", "Unknown"),
                        signature_algorithm=details.get("SignatureAlgorithm", "Unknown"),
                        key_size=2048, # ACM default, hard to get without GetCertificate
                        valid_from=details["NotBefore"],
                        valid_to=details["NotAfter"],
                        chain_status=status_map.get(details["Status"], CertificateStatus.UNTRUSTED),
                        source="AWS ACM",
                        issuance_type=details.get("Type", "IMPORTED"),
                        associated_asset=str(details.get("InUseBy", []))
                    ))
                except Exception as e:
                    print(f"Error processing cert {c['CertificateArn']}: {e}")
        return certs

    def run(self) -> IngestRequest:
        print(f"Starting AWS Discovery in {self.region}...")
        keys = self.collect_keys()
        certs = self.collect_certificates()
        print(f"Found {len(keys)} keys and {len(certs)} certificates.")
        return IngestRequest(keys=keys, certificates=certs)

if __name__ == "__main__":
    # Test run
    collector = AWSCollector()
    # Note: This will fail without AWS creds, but verifies the code structure.
    try:
        data = collector.run()
        print(data.json(indent=2))
    except Exception as e:
        print(f"Collector failed (expected if no creds): {e}")
