# Implementation Plan - Operationalization

## Goal Description
Deploy the Cryptographic Asset Discovery Tool and configure it for ongoing operation. This involves verifying credentials, starting the central Hub service, and scheduling the collectors to run periodically.

## User Review Required
> [!IMPORTANT]
> **Credentials**: I cannot interactively enter passwords. I will create a validation script (`ops/check_creds.py`) to verify if your environment is correctly configured for AWS, Azure, and GCP. If credentials are missing, I will provide instructions.
> **Deployment**: The Hub will be started as a background process.
> **Scheduling**: I will generate a `crontab` snippet.

## Proposed Changes

### Operations Scripts
#### [NEW] [ops/check_creds.py](file:///Users/amitkumarthakur/Downloads/Discovery%20Tool/ops/check_creds.py)
- Python script to check:
    - `~/.aws/credentials` existence.
    - `az account show` success.
    - `GOOGLE_APPLICATION_CREDENTIALS` env var.

#### [NEW] [ops/start_hub.sh](file:///Users/amitkumarthakur/Downloads/Discovery%20Tool/ops/start_hub.sh)
- Shell script to start the FastAPI hub using `nohup` or similar, logging to `hub.log`.

#### [NEW] [ops/schedule_collectors.sh](file:///Users/amitkumarthakur/Downloads/Discovery%20Tool/ops/schedule_collectors.sh)
- Shell script that runs all collectors sequentially (AWS -> Azure -> GCP) and then triggers the report generation.

#### [NEW] [ops/crontab.txt](file:///Users/amitkumarthakur/Downloads/Discovery%20Tool/ops/crontab.txt)
- A crontab entry example to run `schedule_collectors.sh` daily at midnight.

## Verification Plan
- Run `ops/check_creds.py` to see current status.
- Run `ops/start_hub.sh` and check `curl localhost:8000/docs`.
- Run `ops/schedule_collectors.sh` manually to confirm it works.
