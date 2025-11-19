from google.cloud import kms
from google.cloud import asset_v1
from typing import List
from datetime import datetime
from src.hub.schemas import CryptographicKey, DigitalCertificate, Environment, KeyState, CertificateStatus, IngestRequest

class GCPCollector:
    def __init__(self, project_id: str, location_id: str = "global"):
        self.project_id = project_id
        self.location_id = location_id
        self.kms_client = kms.KeyManagementServiceClient()
        # Asset client for broader discovery if needed, but using KMS direct for detail here

    def collect_keys(self) -> List[CryptographicKey]:
        keys = []
        parent = f"projects/{self.project_id}/locations/{self.location_id}"
        
        try:
            # List Key Rings
            for ring in self.kms_client.list_key_rings(request={"parent": parent}):
                # List Crypto Keys
                for key in self.kms_client.list_crypto_keys(request={"parent": ring.name}):
                    # Get primary version for state
                    version = None
                    if key.primary.name:
                        version = key.primary

                    state_map = {
                        kms.CryptoKeyVersion.CryptoKeyVersionState.ENABLED: KeyState.ENABLED,
                        kms.CryptoKeyVersion.CryptoKeyVersionState.DISABLED: KeyState.DISABLED,
                        kms.CryptoKeyVersion.CryptoKeyVersionState.DESTROY_SCHEDULED: KeyState.PENDING_DELETION,
                    }
                    
                    current_state = KeyState.UNAVAILABLE
                    if version:
                        current_state = state_map.get(version.state, KeyState.UNAVAILABLE)

                    keys.append(CryptographicKey(
                        key_id=key.name,
                        name=key.name.split("/")[-1],
                        environment=Environment.GCP,
                        key_type=str(key.purpose),
                        algorithm=str(version.algorithm) if version else "UNKNOWN",
                        state=current_state,
                        creation_date=key.create_time,
                        rotation_enabled=bool(key.rotation_period),
                        rotation_interval_days=key.rotation_period.seconds // 86400 if key.rotation_period else None,
                        last_rotated=key.next_rotation_time, # GCP gives next, can infer last or use next
                        expiry_date=None, # KMS keys don't expire in the traditional sense
                        customer_managed=True,
                        usage=str(key.purpose),
                        last_accessed=None
                    ))
        except Exception as e:
            print(f"Error collecting GCP keys: {e}")
            
        return keys

    # Note: GCP Certificate Manager is a separate API. 
    # For brevity in this prototype, we are focusing on KMS.
    def collect_certificates(self) -> List[DigitalCertificate]:
        return []

    def run(self) -> IngestRequest:
        print(f"Starting GCP Discovery for Project: {self.project_id}...")
        keys = self.collect_keys()
        certs = self.collect_certificates()
        print(f"Found {len(keys)} keys and {len(certs)} certificates.")
        return IngestRequest(keys=keys, certificates=certs)
