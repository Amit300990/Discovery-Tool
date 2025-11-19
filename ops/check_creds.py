import os
import sys
import subprocess

def check_aws():
    print("Checking AWS Credentials...")
    aws_path = os.path.expanduser("~/.aws/credentials")
    if os.path.exists(aws_path):
        print(f"  [OK] Found {aws_path}")
        # Try a simple command
        try:
            subprocess.run(["aws", "sts", "get-caller-identity"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("  [OK] AWS CLI is authenticated.")
            return True
        except FileNotFoundError:
             print("  [WARN] AWS CLI not installed.")
        except subprocess.CalledProcessError:
            print("  [FAIL] AWS CLI installed but not authenticated (check 'aws configure').")
    else:
        print("  [FAIL] No ~/.aws/credentials found.")
    return False

def check_azure():
    print("\nChecking Azure Credentials...")
    try:
        # Check if logged in
        result = subprocess.run(["az", "account", "show"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("  [OK] Azure CLI is authenticated.")
        return True
    except FileNotFoundError:
        print("  [WARN] Azure CLI ('az') not installed.")
    except subprocess.CalledProcessError:
        print("  [FAIL] Azure CLI not logged in (run 'az login').")
    return False

def check_gcp():
    print("\nChecking GCP Credentials...")
    gcp_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if gcp_creds:
        if os.path.exists(gcp_creds):
            print(f"  [OK] GOOGLE_APPLICATION_CREDENTIALS set to {gcp_creds}")
            return True
        else:
            print(f"  [FAIL] Env var set but file not found: {gcp_creds}")
    else:
        # Check gcloud auth
        try:
            subprocess.run(["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("  [OK] gcloud active account found.")
            return True
        except FileNotFoundError:
            print("  [WARN] gcloud CLI not installed.")
        except subprocess.CalledProcessError:
             print("  [FAIL] GOOGLE_APPLICATION_CREDENTIALS not set and no active gcloud account.")
    return False

if __name__ == "__main__":
    print("--- Credential Validation ---")
    aws = check_aws()
    azure = check_azure()
    gcp = check_gcp()
    
    print("\n--- Summary ---")
    print(f"AWS:   {'READY' if aws else 'NOT READY'}")
    print(f"Azure: {'READY' if azure else 'NOT READY'}")
    print(f"GCP:   {'READY' if gcp else 'NOT READY'}")
