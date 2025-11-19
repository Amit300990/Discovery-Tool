from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
from azure.keyvault.certificates import CertificateClient
from typing import List
from datetime import datetime
from src.hub.schemas import CryptographicKey, DigitalCertificate, Environment, KeyState, CertificateStatus, IngestRequest

class AzureCollector:
    def __init__(self, vault_url: str):
        self.vault_url = vault_url
        self.credential = DefaultAzureCredential()
        self.key_client = KeyClient(vault_url=vault_url, credential=self.credential)
        self.cert_client = CertificateClient(vault_url=vault_url, credential=self.credential)

    def collect_keys(self) -> List[CryptographicKey]:
        keys = []
        try:
            # List properties of all keys
            key_properties = self.key_client.list_properties_of_keys()
            for p in key_properties:
                try:
                    # Get full key details for rotation info etc.
                    key = self.key_client.get_key(p.name)
                    
                    keys.append(CryptographicKey(
                        key_id=key.id,
                        name=key.name,
                        environment=Environment.AZURE,
                        key_type=str(key.key_type),
                        algorithm=f"{key.key_type}", # Azure combines type and size often e.g. RSA-2048
                        state=KeyState.ENABLED if key.properties.enabled else KeyState.DISABLED,
                        creation_date=key.properties.created_on,
                        rotation_enabled=False, # Azure Key Vault rotation is a separate policy object, complex to fetch in basic collector
                        rotation_interval_days=None,
                        last_rotated=key.properties.updated_on, # Approximation
                        expiry_date=key.properties.expires_on,
                        customer_managed=True,
                        usage=str(key.key_operations),
                        last_accessed=None
                    ))
                except Exception as e:
                    print(f"Error processing key {p.name}: {e}")
        except Exception as e:
            print(f"Error listing keys in vault {self.vault_url}: {e}")
        return keys

    def collect_certificates(self) -> List[DigitalCertificate]:
        certs = []
        try:
            cert_properties = self.cert_client.list_properties_of_certificates()
            for p in cert_properties:
                try:
                    # Get full cert details
                    cert = self.cert_client.get_certificate(p.name)
                    policy = self.cert_client.get_certificate_policy(p.name)
                    
                    # Determine Status
                    now = datetime.now(datetime.timezone.utc)
                    status = CertificateStatus.VALID
                    if p.expires_on and p.expires_on < now:
                        status = CertificateStatus.EXPIRED
                    elif not p.enabled:
                        status = CertificateStatus.REVOKED # Or disabled

                    certs.append(DigitalCertificate(
                        common_name=policy.subject_name.replace("CN=", ""),
                        san_entries=policy.san_dns_names if policy.san_dns_names else [],
                        serial_number=p.x509_thumbprint.hex(), # Azure doesn't easily expose serial in basic view, using thumbprint as proxy ID
                        issuer=policy.issuer_name,
                        signature_algorithm="Unknown", # Requires downloading CER
                        key_size=policy.key_size if policy.key_size else 2048,
                        valid_from=p.created_on, # Approx
                        valid_to=p.expires_on,
                        chain_status=status,
                        source=f"Azure KV: {self.vault_url}",
                        issuance_type="Manual" if policy.issuer_name == "Unknown" else "Automated",
                        associated_asset=None
                    ))
                except Exception as e:
                    print(f"Error processing cert {p.name}: {e}")
        except Exception as e:
            print(f"Error listing certs in vault {self.vault_url}: {e}")
        return certs

    def run(self) -> IngestRequest:
        print(f"Starting Azure Discovery for Vault: {self.vault_url}...")
        keys = self.collect_keys()
        certs = self.collect_certificates()
        print(f"Found {len(keys)} keys and {len(certs)} certificates.")
        return IngestRequest(keys=keys, certificates=certs)
