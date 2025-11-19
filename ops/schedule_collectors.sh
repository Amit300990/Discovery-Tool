#!/bin/bash
# Run all collectors and generate report
cd "$(dirname "$0")/.."

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
echo "[$TIMESTAMP] Starting Scheduled Discovery..." >> discovery.log

# 1. AWS
echo "Running AWS Collector..."
python3 src/collectors/aws_collector.py >> discovery.log 2>&1

# 2. Azure
echo "Running Azure Collector..."
python3 src/collectors/azure_collector.py >> discovery.log 2>&1

# 3. GCP
echo "Running GCP Collector..."
python3 src/collectors/gcp_collector.py >> discovery.log 2>&1

# 4. Generate Report
echo "Generating Report..."
python3 src/reporting/excel_generator.py >> discovery.log 2>&1

echo "[$TIMESTAMP] Discovery Completed." >> discovery.log
