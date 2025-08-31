# Microsoft Fabric Migration Guide

This guide helps you migrate your MLB data pipeline from SQL Server to Microsoft Fabric.

## 🎯 Overview

The Fabric version includes:
- **Enhanced Connection**: `fabric_connection.py` - Azure AD authentication for Fabric SQL Endpoints
- **Enhanced Loader**: `fabric_json_loader.py` - Transaction-safe loading with stolen base statistics  
- **Enhanced Script**: `load_fabric_date_range_data.py` - Complete date range loading for Fabric
- **Setup Tool**: `setup_fabric.py` - Validates connection and creates tables

## 🚀 Quick Start

### 1. Configure Environment

Copy the template and configure your Fabric details:
```bash
copy .env.fabric.template .env
```

Edit `.env` with your Fabric information:
```bash
FABRIC_SERVER=your-workspace.datawarehouse.fabric.microsoft.com
FABRIC_DATABASE=mlb_data
# Optional: Leave blank for integrated auth
FABRIC_USERNAME=your-azure-ad-username@domain.com
FABRIC_PASSWORD=your-azure-ad-password
```

### 2. Test Connection and Setup Tables

```bash
python setup_fabric.py
```

This will:
- ✅ Test your Fabric connection
- 🗃️ Create necessary tables
- 📋 Show migration guidance

### 3. Load Data to Fabric

Load today's games:
```bash
python load_fabric_date_range_data.py --start 2025-08-31 --end 2025-08-31
```

Load historical data:
```bash
python load_fabric_date_range_data.py --start 2025-03-01 --end 2025-08-31
```

## 🔧 Authentication Options

### Option 1: Azure AD Integrated (Recommended)
- Uses your current Windows credentials
- No username/password needed
- Leave `FABRIC_USERNAME` and `FABRIC_PASSWORD` blank

### Option 2: Azure AD Username/Password
- Set `FABRIC_USERNAME` and `FABRIC_PASSWORD`
- Uses ActiveDirectoryPassword authentication

## 📊 Key Features

### Enhanced Statistics
The Fabric version includes all enhanced batting statistics:
- **Basic Stats**: At-bats, runs, hits, RBI, walks, strikeouts
- **Advanced Stats**: Doubles, triples, home runs
- **Base Running**: Stolen bases, caught stealing (newly added!)

### Transaction Safety
- All data loading uses transactions
- Rollback on errors prevents partial data
- Atomic operations ensure data consistency

### Incremental Loading
- Only loads missing dates by default
- Use `--clear` to force reload existing data
- Automatic detection of existing records

## 🔄 Migration Steps

### Step 1: Test New System
```bash
# Test connection
python setup_fabric.py

# Load a small date range
python load_fabric_date_range_data.py --start 2025-08-31 --end 2025-08-31
```

### Step 2: Load Current Data
```bash
# Load all 2025 season data
python load_fabric_date_range_data.py --start 2025-03-01 --end 2025-08-31
```

### Step 3: Verify Data Quality
Compare record counts between SQL Server and Fabric:
- Games table
- Boxscore table  
- Enhanced statistics (doubles, triples, home runs, stolen bases)

### Step 4: Update Scheduled Tasks
Replace your existing loading scripts with the Fabric versions:
- `load_dynamic_date_range_data.py` → `load_fabric_date_range_data.py`

## 🛠️ Troubleshooting

### Connection Issues
- **Invalid server**: Check your Fabric SQL Endpoint URL
- **Authentication failed**: Verify Azure AD credentials or use integrated auth
- **Access denied**: Ensure you have Fabric workspace permissions

### Driver Issues
- Install ODBC Driver 17 for SQL Server if missing
- Update to latest driver version for best Fabric compatibility

### Performance Tips
- Fabric may be slower than local SQL Server
- Use smaller batch sizes (progress every 25 files vs 50)
- Monitor for timeout issues on large transactions

## 📈 Advantages of Fabric

- **Cloud Scale**: Handles larger datasets
- **Integration**: Works with Power BI, Azure services
- **Managed**: No server maintenance required
- **Analytics**: Built-in analytics capabilities
- **Collaboration**: Shared workspace access

## 🔍 File Structure

```
src/database/
├── connection.py           # Original SQL Server connection
├── fabric_connection.py    # New Fabric connection
├── json_to_sql_loader.py   # Original SQL Server loader  
└── fabric_json_loader.py   # New Fabric loader

# Loading Scripts
├── load_dynamic_date_range_data.py  # Original SQL Server script
├── load_fabric_date_range_data.py   # New Fabric script
└── setup_fabric.py                  # Fabric setup and validation

# Configuration
├── .env.fabric.template             # Fabric config template
└── .env                            # Your actual config (create from template)
```

## 🎪 Example Usage

### Daily Loading (Incremental)
```bash
# Load today's games (auto-extracts if needed)
python load_fabric_date_range_data.py --start 2025-08-31 --end 2025-08-31
```

### Weekly Batch Loading
```bash
# Load last week's games  
python load_fabric_date_range_data.py --start 2025-08-24 --end 2025-08-31
```

### Full Season Migration
```bash
# Load entire 2025 season
python load_fabric_date_range_data.py --start 2025-03-01 --end 2025-08-31
```

### Data Refresh
```bash
# Clear and reload specific date range
python load_fabric_date_range_data.py --start 2025-08-01 --end 2025-08-31 --clear
```

### Preview Mode
```bash
# See what would be loaded without actually loading
python load_fabric_date_range_data.py --start 2025-08-01 --end 2025-08-31 --dry-run
```
