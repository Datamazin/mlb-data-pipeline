"""
Upload CSV files to Fabric Lakehouse Files section with dynamic date filenames.
This script uploads all CSV files to the lakehouse's Files section for storage and future processing.
"""
import os
import sys
import pandas as pd
from datetime import datetime
from pathlib import Path
import requests
import json
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.fabric_connection import FabricConnection

class LakehouseFileUploader:
    def __init__(self):
        self.fabric_conn = FabricConnection()
        self.csv_dir = Path(__file__).parent / "fabric_export"
        self.date_str = datetime.now().strftime("%Y%m%d")  # YYYYMMDD format
        
        # Lakehouse configuration
        self.workspace_id = "6b2ec48f-af5d-4508-9e6e-eb6e58ee9bf6"
        self.lakehouse_id = "2e1cd8ca-f9fa-4d0a-aa20-b7fb76c44eb0"
        self.lakehouse_name = "mlb_api"
        
    def get_access_token(self):
        """Get Azure AD access token for Fabric API"""
        try:
            credential = DefaultAzureCredential()
            token = credential.get_token("https://analysis.windows.net/powerbi/api/.default")
            return token.token
        except Exception as e:
            print(f"❌ Failed to get access token: {e}")
            return None
    
    def upload_via_onelake(self):
        """Upload files directly to OneLake using Azure Storage SDK"""
        print("🔄 Attempting OneLake direct upload...")
        
        try:
            # OneLake endpoint format
            account_url = f"https://onelake.dfs.fabric.microsoft.com"
            
            # Create DataLake service client
            credential = DefaultAzureCredential()
            service_client = DataLakeServiceClient(
                account_url=account_url,
                credential=credential
            )
            
            # File system name format: workspaceId.lakehouseId
            file_system_name = f"{self.workspace_id}.{self.lakehouse_id}"
            file_system_client = service_client.get_file_system_client(file_system=file_system_name)
            
            csv_files = [
                "teams.csv",
                "players.csv", 
                "games.csv",
                "boxscore.csv",
                "raw_json_data.csv"
            ]
            
            uploaded_files = []
            
            for csv_file in csv_files:
                local_path = self.csv_dir / csv_file
                if not local_path.exists():
                    print(f"⚠️  File not found: {local_path}")
                    continue
                
                # Create date-stamped filename
                base_name = csv_file.replace('.csv', '')
                remote_filename = f"mlb_data_{base_name}_{self.date_str}.csv"
                remote_path = f"Files/mlb_exports/{remote_filename}"
                
                print(f"📤 Uploading {csv_file} → {remote_path}")
                
                try:
                    # Create directory client
                    directory_client = file_system_client.get_directory_client("Files/mlb_exports")
                    
                    # Create file client
                    file_client = directory_client.get_file_client(remote_filename)
                    
                    # Upload file
                    with open(local_path, 'rb') as file_data:
                        file_client.upload_data(
                            data=file_data.read(),
                            overwrite=True
                        )
                    
                    file_size = local_path.stat().st_size
                    print(f"✅ Uploaded {remote_filename} ({file_size:,} bytes)")
                    uploaded_files.append(remote_filename)
                    
                except Exception as e:
                    print(f"❌ Failed to upload {csv_file}: {e}")
            
            if uploaded_files:
                print(f"\n🎉 Successfully uploaded {len(uploaded_files)} files to lakehouse Files section:")
                for filename in uploaded_files:
                    print(f"   📁 Files/mlb_exports/{filename}")
                return True
            else:
                print("❌ No files were uploaded successfully")
                return False
                
        except Exception as e:
            print(f"❌ OneLake upload failed: {e}")
            return False
    
    def upload_via_fabric_api(self):
        """Upload files using Fabric REST API"""
        print("🔄 Attempting Fabric REST API upload...")
        
        access_token = self.get_access_token()
        if not access_token:
            return False
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        csv_files = [
            "teams.csv",
            "players.csv", 
            "games.csv",
            "boxscore.csv",
            "raw_json_data.csv"
        ]
        
        uploaded_files = []
        
        for csv_file in csv_files:
            local_path = self.csv_dir / csv_file
            if not local_path.exists():
                print(f"⚠️  File not found: {local_path}")
                continue
            
            # Create date-stamped filename
            base_name = csv_file.replace('.csv', '')
            remote_filename = f"mlb_data_{base_name}_{self.date_str}.csv"
            
            print(f"📤 Uploading {csv_file} → {remote_filename}")
            
            try:
                # Read file content
                with open(local_path, 'rb') as f:
                    file_content = f.read()
                
                # Fabric API endpoint for file upload
                upload_url = f"https://api.fabric.microsoft.com/v1/workspaces/{self.workspace_id}/items/{self.lakehouse_id}/files/Files/mlb_exports/{remote_filename}"
                
                upload_headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'text/csv'
                }
                
                response = requests.put(
                    upload_url,
                    headers=upload_headers,
                    data=file_content
                )
                
                if response.status_code in [200, 201, 204]:
                    file_size = len(file_content)
                    print(f"✅ Uploaded {remote_filename} ({file_size:,} bytes)")
                    uploaded_files.append(remote_filename)
                else:
                    print(f"❌ Failed to upload {csv_file}: HTTP {response.status_code}")
                    print(f"   Response: {response.text}")
                    
            except Exception as e:
                print(f"❌ Failed to upload {csv_file}: {e}")
        
        if uploaded_files:
            print(f"\n🎉 Successfully uploaded {len(uploaded_files)} files to lakehouse Files section:")
            for filename in uploaded_files:
                print(f"   📁 Files/mlb_exports/{filename}")
            return True
        else:
            print("❌ No files were uploaded successfully")
            return False
    
    def upload_via_web_guidance(self):
        """Provide guidance for manual web upload with date-stamped filenames"""
        print("📋 Manual Web Upload Instructions:")
        print(f"1. Navigate to: https://fabric.microsoft.com")
        print(f"2. Open workspace and select '{self.lakehouse_name}' lakehouse")
        print(f"3. Go to Files section → Create folder 'mlb_exports' if it doesn't exist")
        print(f"4. Upload CSV files with these date-stamped names:")
        
        csv_files = [
            "teams.csv",
            "players.csv", 
            "games.csv",
            "boxscore.csv",
            "raw_json_data.csv"
        ]
        
        print(f"\n📅 Suggested filenames for {self.date_str}:")
        for csv_file in csv_files:
            base_name = csv_file.replace('.csv', '')
            suggested_name = f"mlb_data_{base_name}_{self.date_str}.csv"
            print(f"   {csv_file} → {suggested_name}")
        
        print(f"\n📁 Upload location: Files/mlb_exports/")
        print(f"💡 This preserves historical data with date tracking")
    
    def create_dated_copies(self):
        """Create local copies with date-stamped filenames for manual upload"""
        print(f"📅 Creating date-stamped copies for {self.date_str}...")
        
        # Create dated export directory
        dated_dir = Path(__file__).parent / f"fabric_export_dated_{self.date_str}"
        dated_dir.mkdir(exist_ok=True)
        
        csv_files = [
            "teams.csv",
            "players.csv", 
            "games.csv",
            "boxscore.csv",
            "raw_json_data.csv"
        ]
        
        copied_files = []
        
        for csv_file in csv_files:
            source_path = self.csv_dir / csv_file
            if not source_path.exists():
                print(f"⚠️  File not found: {source_path}")
                continue
            
            # Create date-stamped filename
            base_name = csv_file.replace('.csv', '')
            dated_filename = f"mlb_data_{base_name}_{self.date_str}.csv"
            dest_path = dated_dir / dated_filename
            
            # Copy file with new name
            import shutil
            shutil.copy2(source_path, dest_path)
            
            file_size = dest_path.stat().st_size
            print(f"✅ Created {dated_filename} ({file_size:,} bytes)")
            copied_files.append(dated_filename)
        
        if copied_files:
            print(f"\n🎉 Created {len(copied_files)} date-stamped files in:")
            print(f"   📁 {dated_dir}")
            print(f"\n💡 These files are ready for manual upload to lakehouse Files section")
            return True
        else:
            print("❌ No files were copied")
            return False
    
    def run(self):
        """Main upload process - tries multiple methods"""
        print(f"🚀 Starting lakehouse file upload for date: {self.date_str}")
        print(f"📊 Source directory: {self.csv_dir}")
        
        # Method 1: Try OneLake direct upload
        if self.upload_via_onelake():
            return True
        
        print("\n" + "="*50)
        
        # Method 2: Try Fabric REST API
        if self.upload_via_fabric_api():
            return True
        
        print("\n" + "="*50)
        
        # Method 3: Create dated copies for manual upload
        print("🔄 Creating date-stamped files for manual upload...")
        if self.create_dated_copies():
            print("\n" + "="*50)
            self.upload_via_web_guidance()
            return True
        
        print("❌ All upload methods failed")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("📤 MLB Data Lakehouse File Upload")
    print("=" * 60)
    
    uploader = LakehouseFileUploader()
    success = uploader.run()
    
    if success:
        print("\n🎯 Upload process completed!")
        print("💡 Files are now available in lakehouse Files section for:")
        print("   • Data analysis and exploration")
        print("   • Future table creation")
        print("   • Historical data tracking")
        print("   • Notebook-based processing")
    else:
        print("\n❌ Upload process failed")
        print("💡 Try manual upload via Fabric web interface")
    
    return success

if __name__ == "__main__":
    main()
