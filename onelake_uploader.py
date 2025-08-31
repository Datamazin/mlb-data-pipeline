#!/usr/bin/env python3
"""
Advanced OneLake Uploader for MLB Data
=====================================

Upload CSV files directly to OneLake using Azure Storage SDK.
Requires: pip install azure-storage-file-datalake azure-identity
"""

import os
from azure.storage.filedatalake import DataLakeServiceClient
from azure.identity import DefaultAzureCredential
from pathlib import Path

def upload_to_onelake():
    """Upload CSV files to OneLake."""

    # OneLake connection details
    workspace_id = os.getenv('FABRIC_WORKSPACE_ID')
    lakehouse_id = os.getenv('FABRIC_LAKEHOUSE_ID') 

    if not workspace_id or not lakehouse_id:
        print("Missing OneLake configuration")
        print("Add to .env file:")
        print("FABRIC_WORKSPACE_ID=your_workspace_id")
        print("FABRIC_LAKEHOUSE_ID=your_lakehouse_id")
        return False

    # OneLake endpoint
    account_url = f"https://onelake.dfs.fabric.microsoft.com"

    # Initialize client with Azure AD credentials
    credential = DefaultAzureCredential()
    service_client = DataLakeServiceClient(account_url, credential=credential)

    # Get file system (lakehouse)
    file_system_name = f"{workspace_id}.{lakehouse_id}"
    file_system_client = service_client.get_file_system_client(file_system_name)

    # Upload each CSV file
    export_dir = Path("fabric_export")
    csv_files = list(export_dir.glob("*.csv"))

    for csv_file in csv_files:
        print(f"Uploading {csv_file.name}...")

        # Upload to Files/mlb_data/ directory
        file_path = f"Files/mlb_data/{csv_file.name}"
        file_client = file_system_client.get_file_client(file_path)

        with open(csv_file, 'rb') as data:
            file_client.upload_data(data, overwrite=True)

        print(f"   {csv_file.name} uploaded successfully")

    print("All files uploaded to OneLake!")
    return True

if __name__ == "__main__":
    upload_to_onelake()
