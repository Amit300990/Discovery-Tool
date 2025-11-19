import requests
import time
import subprocess
import sys
import os
from datetime import datetime, timedelta

# Ensure we are in the project root
os.chdir("/Users/amitkumarthakur/Downloads/Discovery Tool")

def run_verification():
    print("--- Starting Verification ---")
    
    # 1. Start Hub API
    print("Starting Hub API...")
    hub_process = subprocess.Popen(
        [sys.executable, "-m", "src.hub.main"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(5) # Wait for startup

    try:
        # 2. Simulate Data Ingestion
        print("Simulating Data Ingestion...")
        payload = {
            "keys": [
                {
                    "key_id": "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012",
                    "name": "alias/test-key",
                    "environment": "AWS",
                    "key_type": "ENCRYPT_DECRYPT",
                    "algorithm": "RSA-4096",
                    "state": "Enabled",
                    "creation_date": datetime.now().isoformat(),
                    "rotation_enabled": True,
                    "rotation_interval_days": 365,
                    "last_rotated": (datetime.now() - timedelta(days=100)).isoformat(),
                    "expiry_date": None,
                    "customer_managed": True,
                    "usage": "EBS Encryption",
                    "last_accessed": datetime.now().isoformat()
                }
            ],
            "certificates": [
                {
                    "common_name": "test.example.com",
                    "san_entries": ["www.test.example.com"],
                    "serial_number": "00:11:22:33:44",
                    "issuer": "Test CA",
                    "signature_algorithm": "SHA256withRSA",
                    "key_size": 2048,
                    "valid_from": datetime.now().isoformat(),
                    "valid_to": (datetime.now() + timedelta(days=20)).isoformat(), # Expiring soon
                    "chain_status": "Valid",
                    "source": "Manual Test",
                    "issuance_type": "Manual",
                    "associated_asset": "Load Balancer"
                }
            ]
        }
        
        response = requests.post("http://localhost:8000/ingest", json=payload)
        if response.status_code == 201:
            print("Ingestion Successful!")
        else:
            print(f"Ingestion Failed: {response.text}")
            return

        # 3. Generate Report
        print("Generating Excel Report...")
        subprocess.run([sys.executable, "src/reporting/excel_generator.py"], check=True)
        
        if os.path.exists("Cryptographic_Asset_Inventory.xlsx"):
            print("Report generated successfully: Cryptographic_Asset_Inventory.xlsx")
        else:
            print("Report generation failed.")

    finally:
        print("Stopping Hub API...")
        hub_process.terminate()
        hub_process.wait()

if __name__ == "__main__":
    run_verification()
