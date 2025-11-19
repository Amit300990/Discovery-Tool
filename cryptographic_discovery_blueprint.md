# Cryptographic Asset Discovery Blueprint

**Version:** 1.0
**Date:** November 2025
**Status:** Final Draft

---

## 1. Scope Definition

This blueprint defines the strategy for discovering, inventorying, and analyzing cryptographic assets across the hybrid cloud estate. The scope encompasses all identifiable keys, certificates, and secrets within the following environments:

### 1.1 On-Premises Infrastructure
*   **Hardware Security Modules (HSMs):** Thales, Entrust, Utimaco (Network & PCIe).
*   **Public Key Infrastructure (PKI):** Microsoft Active Directory Certificate Services (AD CS), EJBCA, Offline Root CAs.
*   **Operating Systems:**
    *   **Linux:** `/etc/ssl`, `/etc/pki`, Java Keystores (JKS), OpenSSL directories.
    *   **Windows:** CAPI, CNG, IIS Certificate Stores, Personal/Machine Stores.
*   **Network Infrastructure:**
    *   **Load Balancers:** F5 BIG-IP, Citrix ADC (NetScaler).
    *   **Firewalls:** Palo Alto, Cisco ASA/Firepower, Fortinet.
    *   **Switches/Routers:** SSH host keys, device certificates.
*   **Application Servers:** Apache, Nginx, Tomcat, WebLogic, JBoss.

### 1.2 Amazon Web Services (AWS)
*   **KMS:** Customer Managed Keys (CMK), AWS Managed Keys.
*   **ACM:** Public Certificates, Private CA Certificates.
*   **CloudHSM:** Clusters and Keys.
*   **Secrets Manager:** Secrets (API keys, DB credentials, SSH keys).
*   **Systems Manager Parameter Store:** SecureString parameters.
*   **IAM:** Server Certificates (legacy), Access Keys (signing).

### 1.3 Microsoft Azure
*   **Key Vault:** Keys, Secrets, Certificates.
*   **App Service:** SSL/TLS Certificates (App Service Managed & Uploaded).
*   **Managed HSM:** Dedicated HSM keys.
*   **Virtual Machines:** Certificates stored within IaaS VM OS (see On-Prem OS scope).

### 1.4 Google Cloud Platform (GCP)
*   **Cloud KMS:** Key Rings, Crypto Keys, Crypto Key Versions.
*   **Certificate Manager:** Managed and Self-managed certificates.
*   **Secret Manager:** Secrets and versions.
*   **Compute Engine:** SSH keys, Shielded VM identity keys.

### 1.5 VMware Cloud (VMC) & vSphere
*   **vCenter Server:** Machine SSL certs, Solution User certs, STS signing certs.
*   **ESXi Hosts:** Host certificates.
*   **NSX-T:** Manager certs, VIP certs, Principal Identity certs.
*   **vSAN:** Data-at-rest encryption keys (KMS provider integration).

---

## 2. Required Outputs

The discovery process must normalize data into the following schema to ensure consistent reporting and risk analysis.

### 2.1 Cryptographic Keys Schema

| Field | Description | Example |
| :--- | :--- | :--- |
| **Key ID** | Unique identifier (ARN, URL, UUID) | `arn:aws:kms:us-east-1:123:key/abc-123` |
| **Name/Alias** | Human-readable name | `alias/production-db-key` |
| **Environment** | Cloud Provider or On-Prem | `AWS` |
| **Key Type** | Cryptographic family | `RSA`, `ECC`, `AES` |
| **Algorithm & Size** | Specific algo and bit length | `RSA-4096`, `AES-256-GCM` |
| **State** | Current lifecycle state | `Enabled`, `Disabled`, `PendingDeletion` |
| **Creation Date** | Timestamp of creation | `2023-01-15T08:00:00Z` |
| **Rotation Status** | Auto-rotation enabled? | `True` |
| **Rotation Interval** | Days between rotation | `365` |
| **Last Rotated** | Timestamp of last rotation | `2024-01-15T08:00:00Z` |
| **Expiry Date** | If applicable (material expiry) | `N/A` |
| **Management** | Customer vs. Provider Managed | `Customer Managed` |
| **Usage** | Linked resources or services | `EBS Volume vol-0123`, `RDS db-prod` |
| **Last Accessed** | Timestamp of last crypto op | `2025-11-19T10:00:00Z` |

### 2.2 Digital Certificates Schema

| Field | Description | Example |
| :--- | :--- | :--- |
| **Common Name (CN)** | Subject Common Name | `www.example.com` |
| **SAN Entries** | Subject Alternative Names | `api.example.com`, `auth.example.com` |
| **Serial Number** | Hex serial number | `00:AB:CD:EF...` |
| **Issuer** | Issuing CA Name | `DigiCert Global Root G2` |
| **Signature Algo** | Signing algorithm | `SHA256withRSA` |
| **Key Size** | Public key size | `2048` |
| **Valid From** | Start of validity | `2024-01-01T00:00:00Z` |
| **Valid To** | Expiry date | `2025-01-01T00:00:00Z` |
| **Days to Expiry** | Calculated field | `42` |
| **Chain Status** | Validation result | `Valid`, `Untrusted Root`, `Expired` |
| **Source** | Where it was found | `AWS ACM`, `IIS Store`, `F5 LTM` |
| **Issuance Type** | Method of issuance | `ACME`, `Manual`, `Auto-Enrollment` |
| **Associated Asset** | Where it is installed | `lb-prod-01 (192.168.1.50)` |

### 2.3 Export Requirements
*   **Format:** Unified Excel Workbook (`.xlsx`).
*   **Structure:**
    *   **Tab 1: Dashboard:** High-level metrics (Total Assets, Expiring <30d, Non-Compliant Algos).
    *   **Tab 2: Keys Inventory:** Pivot-table ready, filterable by Cloud/Region.
    *   **Tab 3: Certificates Inventory:** Pivot-table ready, filterable by Issuer/Expiry.
    *   **Tab 4: Secrets Inventory:** Metadata only (never values).

---

## 3. Discovery Methods per Environment

### 3.1 Amazon Web Services (AWS)
*   **Method:** AWS SDK (Boto3) / CLI.
*   **Auth:** IAM Role with `SecurityAudit` + custom inline policy for `List` actions on KMS/Secrets.
*   **Rate Limits:** Handle `ThrottlingException` with exponential backoff.
*   **Pagination:** Use `NextToken` or Paginators in Boto3.
*   **Key APIs:**
    *   **KMS:** `ListKeys`, `DescribeKey` (for metadata), `GetKeyRotationStatus`, `ListResourceTags`.
    *   **ACM:** `ListCertificates`, `DescribeCertificate`, `ListTagsForCertificate`.
    *   **Secrets Manager:** `ListSecrets`, `DescribeSecret` (DO NOT call `GetSecretValue`).

### 3.2 Microsoft Azure
*   **Method:** Azure CLI / Azure SDK for Python.
*   **Auth:** Service Principal (App Registration) with `Key Vault Reader` role on subscriptions.
*   **Key APIs:**
    *   **Key Vault:** `az keyvault key list`, `az keyvault certificate list`, `az keyvault secret list`.
    *   **Graph API:** For App Service certificates if not in KV.
*   **Scope:** Iterate through all Resource Groups and Subscriptions.

### 3.3 Google Cloud Platform (GCP)
*   **Method:** Cloud Asset Inventory API + Cloud KMS API.
*   **Auth:** Service Account with `cloudkms.viewer` and `cloudasset.viewer` roles.
*   **Key APIs:**
    *   **KMS:** `projects.locations.keyRings.cryptoKeys.list`, `get` for version details.
    *   **Certificate Manager:** `projects.locations.certificates.list`.
*   **Optimization:** Use Cloud Asset Inventory export for bulk metadata fetching to avoid API throttling.

### 3.4 VMware Cloud & vSphere
*   **Method:** vSphere Automation SDK (REST API).
*   **Auth:** Service Account with Read-Only permissions (Global).
*   **Key APIs:**
    *   **vCenter:** `/api/vcenter/certificate-management/vcenter/tls` (Machine SSL).
    *   **Trust Store:** `/api/vcenter/certificate-management/vcenter/trusted-root-chains`.
    *   **NSX-T:** `/api/v1/trust-management/certificates`.

### 3.5 On-Premises (Agent-Based & Network Scanning)
*   **Network Scanning:**
    *   **Tool:** Authenticated scanner (e.g., Nessus, Qualys) or custom Python script using `ssl` module.
    *   **Target:** Subnets (443, 8443, etc.).
    *   **Method:** TLS Handshake to capture leaf and chain.
*   **Windows Agents:**
    *   **Command:** PowerShell `Get-ChildItem Cert:\LocalMachine\My -Recurse`.
    *   **AD CS:** `CertView` command to dump CA database headers.
*   **Linux Agents:**
    *   **Command:** `find / -name "*.pem" -o -name "*.crt" -o -name "*.key"` (with exclusion paths).
    *   **Java:** `keytool -list -v -keystore <path>`.

---

## 4. Architecture for Centralized Collection

### 4.1 System Design
The architecture follows a **Hub-and-Spoke** model.

1.  **Collectors (Spokes):**
    *   **Cloud Collectors:** Serverless functions (AWS Lambda, Azure Functions) triggered on schedule (e.g., nightly). They query cloud APIs and push JSON payloads to the Hub.
    *   **On-Prem Collector:** A dedicated VM or container running the discovery agent. Performs network scans and AD CS queries. Pushes data to the Hub via HTTPS.

2.  **Ingestion (Hub):**
    *   **Endpoint:** Secure API Gateway (mTLS auth).
    *   **Queue:** Kafka or SQS to buffer incoming discovery data.

3.  **Processing Pipeline:**
    *   **Normalization:** Python workers parse raw JSON from different providers and map fields to the Unified Schema (Section 2).
    *   **Enrichment:** DNS lookups, Owner tagging based on CMDB.

4.  **Storage:**
    *   **Database:** PostgreSQL (for structured querying) or Elasticsearch (for full-text search).
    *   **Encryption:** Database encrypted at rest. Sensitive fields (if any) field-level encrypted.

5.  **Reporting:**
    *   **Generator:** Python `pandas` + `XlsxWriter` job runs weekly to generate the Excel report.

### 4.2 Security & Error Handling
*   **Encryption:** All data in transit TLS 1.3. API keys for collectors stored in Vault/Secrets Manager.
*   **Error Handling:** Dead Letter Queue (DLQ) for failed parsing. Alerting on collector heartbeat failure.
*   **Least Privilege:** Collectors have **Read-Only** access. They strictly cannot retrieve private key material (except for local hash checks if configured).

---

## 5. Risk & Compliance Mapping

| Framework | Control ID | Requirement | Discovery Mapping |
| :--- | :--- | :--- | :--- |
| **NIST 800-57** | Part 1, Sec 5 | Key Management Policy | Identifies key types, states, and rotation cycles. |
| **NIST 800-131A** | Sec 1 | Key Lengths & Algos | Flags keys < 2048-bit RSA or using SHA-1. |
| **PCI DSS 4.0** | 4.2.1 | Strong Cryptography | Verifies strong algos for PAN transmission/storage. |
| **PCI DSS 4.0** | 12.3.3 | Crypto Asset Inventory | Provides the required annual inventory of crypto assets. |
| **ISO 27001:2022** | A.8.24 | Use of Cryptography | Evidence of effective key management and lifecycle. |
| **DORA** | Art. 9 | ICT Security | Maps critical assets to crypto protection mechanisms. |

---

## 6. Excel Reporting Module

### 6.1 Formatting Rules
*   **Header Row:** Bold, Frozen Pane, Dark Blue Background, White Text.
*   **Data Rows:** Alternating light grey/white background.
*   **Dates:** ISO 8601 format (YYYY-MM-DD).

### 6.2 Conditional Formatting (Alerts)
*   **Expiry Date:**
    *   **Red:** `< 30 days` (Critical Action)
    *   **Orange:** `30 - 60 days` (Warning)
    *   **Yellow:** `60 - 90 days` (Notice)
*   **Key Size / Algorithm:**
    *   **Red:** `RSA < 2048`, `SHA-1`, `MD5`, `3DES`.
*   **Rotation:**
    *   **Red:** `Last Rotated > 365 days` (if policy requires annual).

### 6.3 Summary Dashboard (Tab 1)
*   **KPI Cards:**
    *   Total Certificates
    *   Expired / Revoked
    *   Expiring in 30 Days
    *   Weak Algorithms Detected
*   **Charts:**
    *   Pie Chart: Assets by Environment (AWS vs Azure vs On-Prem).
    *   Bar Chart: Certificates by Issuer (DigiCert vs Let's Encrypt vs Internal).

---

## 7. Final Deliverables & Roadmap

### 7.1 Timeline (4-Week Sprint)

*   **Week 1: Setup & Access**
    *   Provision Service Accounts/Roles across clouds.
    *   Deploy On-Prem Collector VM.
    *   Firewall rule configuration.
*   **Week 2: Discovery Execution**
    *   Run Cloud Collectors (AWS, Azure, GCP).
    *   Run Network Scans & AD CS Enumeration.
    *   Initial data ingestion and validation.
*   **Week 3: Analysis & Normalization**
    *   Data cleaning and deduplication.
    *   Enrichment with ownership data.
    *   Compliance mapping analysis.
*   **Week 4: Reporting & Handover**
    *   Generate Final Excel Blueprint.
    *   Executive Presentation Deck.
    *   Workshop: "Maintaining the Inventory".

### 7.2 RACI Matrix

| Task | Security Architect | Cloud Ops | NetSec | Compliance |
| :--- | :---: | :---: | :---: | :---: |
| **Define Scope** | **R/A** | C | C | I |
| **Grant Access** | I | **R** | **R** | I |
| **Deploy Agents** | **R** | C | C | I |
| **Review Data** | **R** | C | I | C |
| **Sign-off** | **A** | I | I | **R** |

*(R=Responsible, A=Accountable, C=Consulted, I=Informed)*

### 7.3 Bill of Materials (BOM)
1.  **Compute:** 1x t3.medium (AWS) or equivalent for On-Prem Collector.
2.  **Storage:** S3 Bucket / Blob Storage for raw logs (approx. 10GB).
3.  **Software:** Python 3.9+, Boto3, Azure Identity SDK, Google Cloud Client, Pandas, XlsxWriter.
4.  **Access:** Read-only Service Principals/IAM Roles.

### 7.4 Risks & Mitigations
*   **Risk:** API Throttling during bulk discovery.
    *   *Mitigation:* Implement exponential backoff and staggered execution.
*   **Risk:** Incomplete On-Prem visibility due to firewalls.
    *   *Mitigation:* Place collectors in core network zones; use authenticated scanning.
*   **Risk:** False Positives in network scanning.
    *   *Mitigation:* Validate against known inventory; manual exclusion lists.

---
