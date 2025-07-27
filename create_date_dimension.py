#!/usr/bin/env python3
"""
Create Date Dimension Table for MLB Data Pipeline
This script creates a comprehensive date dimension table with useful attributes.
"""

import sys
from pathlib import Path
from datetime import datetime, date, timedelta

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.database.connection import DatabaseConnection

def create_date_dimension_table():
    """Create the date dimension table with comprehensive date attributes."""
    
    db = DatabaseConnection()
    try:
        db.connect()
        
        print("📅 CREATING DATE DIMENSION TABLE")
        print("=" * 60)
        
        # Drop table if exists and create new one
        print("1. Creating date dimension table structure...")
        
        create_table_sql = """
        -- Drop table if exists
        IF EXISTS (SELECT * FROM sysobjects WHERE name='dim_date' AND xtype='U')
        DROP TABLE dim_date;
        
        -- Create date dimension table
        CREATE TABLE dim_date (
            date_key INT PRIMARY KEY,                    -- YYYYMMDD format
            full_date DATE NOT NULL,                     -- Actual date
            year INT NOT NULL,                           -- 2025
            quarter INT NOT NULL,                        -- 1, 2, 3, 4
            month INT NOT NULL,                          -- 1-12
            week_of_year INT NOT NULL,                   -- 1-53
            day_of_year INT NOT NULL,                    -- 1-366
            day_of_month INT NOT NULL,                   -- 1-31
            day_of_week INT NOT NULL,                    -- 1=Sunday, 7=Saturday
            
            -- Text descriptions
            year_text NVARCHAR(4) NOT NULL,              -- '2025'
            quarter_text NVARCHAR(10) NOT NULL,          -- 'Q1 2025'
            month_name NVARCHAR(20) NOT NULL,            -- 'January'
            month_name_short NVARCHAR(3) NOT NULL,       -- 'Jan'
            month_year NVARCHAR(20) NOT NULL,            -- 'January 2025'
            day_name NVARCHAR(20) NOT NULL,              -- 'Monday'
            day_name_short NVARCHAR(3) NOT NULL,         -- 'Mon'
            
            -- Business/MLB season attributes
            is_weekend BIT NOT NULL,                     -- 1 if Saturday/Sunday
            is_weekday BIT NOT NULL,                     -- 1 if Monday-Friday
            is_month_start BIT NOT NULL,                 -- 1 if first day of month
            is_month_end BIT NOT NULL,                   -- 1 if last day of month
            is_quarter_start BIT NOT NULL,               -- 1 if first day of quarter
            is_quarter_end BIT NOT NULL,                 -- 1 if last day of quarter
            is_year_start BIT NOT NULL,                  -- 1 if January 1st
            is_year_end BIT NOT NULL,                    -- 1 if December 31st
            
            -- MLB-specific attributes
            mlb_season_year INT,                         -- MLB season year (may differ from calendar year)
            is_mlb_regular_season BIT DEFAULT 0,         -- 1 if during regular season
            is_mlb_spring_training BIT DEFAULT 0,        -- 1 if during spring training
            is_mlb_playoffs BIT DEFAULT 0,               -- 1 if during playoffs
            is_mlb_offseason BIT DEFAULT 0,              -- 1 if during offseason
            mlb_season_phase NVARCHAR(20),               -- 'Regular Season', 'Spring Training', 'Playoffs', 'Offseason'
            
            -- Relative date helpers
            days_from_today INT,                         -- Negative for past, positive for future
            is_past BIT NOT NULL,                        -- 1 if date is in the past
            is_future BIT NOT NULL,                      -- 1 if date is in the future
            is_today BIT NOT NULL,                       -- 1 if date is today
            
            created_at DATETIME DEFAULT GETDATE()
        );
        
        -- Create indexes for performance
        CREATE INDEX IX_dim_date_full_date ON dim_date(full_date);
        CREATE INDEX IX_dim_date_year_month ON dim_date(year, month);
        CREATE INDEX IX_dim_date_mlb_season ON dim_date(mlb_season_year, mlb_season_phase);
        """
        
        db.execute_query(create_table_sql)
        print("   ✅ Date dimension table created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating date dimension table: {e}")
        return False
    finally:
        db.disconnect()

def populate_date_dimension(start_year=2020, end_year=2030):
    """Populate the date dimension table with data."""
    
    db = DatabaseConnection()
    try:
        db.connect()
        
        print(f"2. Populating date dimension from {start_year} to {end_year}...")
        
        # Generate dates
        start_date = date(start_year, 1, 1)
        end_date = date(end_year, 12, 31)
        current_date = start_date
        today = date.today()
        
        batch_size = 100
        batch_data = []
        total_inserted = 0
        
        while current_date <= end_date:
            # Calculate date attributes
            date_key = int(current_date.strftime('%Y%m%d'))
            year = current_date.year
            quarter = ((current_date.month - 1) // 3) + 1
            month = current_date.month
            day_of_month = current_date.day
            day_of_year = current_date.timetuple().tm_yday
            week_of_year = current_date.isocalendar()[1]
            day_of_week = current_date.isoweekday() % 7 + 1  # Convert to 1=Sunday format
            
            # Text descriptions
            month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December']
            month_names_short = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            day_names_short = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
            
            month_name = month_names[month]
            month_name_short = month_names_short[month]
            day_name = day_names[(day_of_week - 1) % 7]
            day_name_short = day_names_short[(day_of_week - 1) % 7]
            
            # Business attributes
            is_weekend = 1 if day_of_week in [1, 7] else 0  # Sunday=1, Saturday=7
            is_weekday = 1 - is_weekend
            
            # Month/quarter/year boundaries
            is_month_start = 1 if day_of_month == 1 else 0
            is_month_end = 1 if (current_date + timedelta(days=1)).day == 1 else 0
            is_quarter_start = 1 if month in [1, 4, 7, 10] and day_of_month == 1 else 0
            is_quarter_end = 1 if month in [3, 6, 9, 12] and is_month_end == 1 else 0
            is_year_start = 1 if month == 1 and day_of_month == 1 else 0
            is_year_end = 1 if month == 12 and day_of_month == 31 else 0
            
            # MLB season logic (approximate dates)
            mlb_season_year = year
            if month >= 10:  # October onwards is next season
                mlb_season_year = year + 1
                
            # MLB season phases (approximate)
            is_mlb_spring_training = 0
            is_mlb_regular_season = 0
            is_mlb_playoffs = 0
            is_mlb_offseason = 0
            mlb_season_phase = 'Offseason'
            
            if month == 2 or (month == 3 and day_of_month < 20):  # Feb - mid March
                is_mlb_spring_training = 1
                mlb_season_phase = 'Spring Training'
            elif (month == 3 and day_of_month >= 20) or month in [4, 5, 6, 7, 8, 9]:  # Mid March - September
                is_mlb_regular_season = 1
                mlb_season_phase = 'Regular Season'
            elif month == 10 or (month == 11 and day_of_month < 15):  # October - mid November
                is_mlb_playoffs = 1
                mlb_season_phase = 'Playoffs'
            else:
                is_mlb_offseason = 1
                mlb_season_phase = 'Offseason'
            
            # Relative to today
            days_from_today = (current_date - today).days
            is_past = 1 if current_date < today else 0
            is_future = 1 if current_date > today else 0
            is_today = 1 if current_date == today else 0
            
            # Prepare batch insert
            batch_data.append((
                date_key, current_date, year, quarter, month, week_of_year, day_of_year, day_of_month, day_of_week,
                str(year), f'Q{quarter} {year}', month_name, month_name_short, f'{month_name} {year}',
                day_name, day_name_short,
                is_weekend, is_weekday, is_month_start, is_month_end, is_quarter_start, is_quarter_end,
                is_year_start, is_year_end,
                mlb_season_year, is_mlb_regular_season, is_mlb_spring_training, is_mlb_playoffs, is_mlb_offseason, mlb_season_phase,
                days_from_today, is_past, is_future, is_today
            ))
            
            # Insert batch when full
            if len(batch_data) >= batch_size:
                insert_batch(db, batch_data)
                total_inserted += len(batch_data)
                if total_inserted % 1000 == 0:
                    print(f"   📅 Inserted {total_inserted} dates...")
                batch_data = []
            
            current_date += timedelta(days=1)
        
        # Insert remaining batch
        if batch_data:
            insert_batch(db, batch_data)
            total_inserted += len(batch_data)
        
        print(f"   ✅ Successfully inserted {total_inserted} dates")
        return True
        
    except Exception as e:
        print(f"❌ Error populating date dimension: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.disconnect()

def insert_batch(db, batch_data):
    """Insert a batch of date records."""
    
    insert_sql = """
    INSERT INTO dim_date (
        date_key, full_date, year, quarter, month, week_of_year, day_of_year, day_of_month, day_of_week,
        year_text, quarter_text, month_name, month_name_short, month_year, day_name, day_name_short,
        is_weekend, is_weekday, is_month_start, is_month_end, is_quarter_start, is_quarter_end, is_year_start, is_year_end,
        mlb_season_year, is_mlb_regular_season, is_mlb_spring_training, is_mlb_playoffs, is_mlb_offseason, mlb_season_phase,
        days_from_today, is_past, is_future, is_today
    ) VALUES """
    
    # Build values clause
    values_list = []
    for data in batch_data:
        values = "(" + ", ".join([f"'{item}'" if isinstance(item, str) or isinstance(item, date) else str(item) for item in data]) + ")"
        values_list.append(values)
    
    full_sql = insert_sql + ", ".join(values_list)
    db.execute_query(full_sql)

def verify_date_dimension():
    """Verify the date dimension table was created and populated correctly."""
    
    db = DatabaseConnection()
    try:
        db.connect()
        
        print("3. Verifying date dimension table...")
        
        # Check total count
        total_count = db.fetch_results("SELECT COUNT(*) FROM dim_date")[0][0]
        print(f"   📊 Total dates: {total_count}")
        
        # Check date range
        date_range = db.fetch_results("SELECT MIN(full_date), MAX(full_date) FROM dim_date")[0]
        print(f"   📅 Date range: {date_range[0]} to {date_range[1]}")
        
        # Check MLB season distribution
        mlb_phases = db.fetch_results("""
        SELECT mlb_season_phase, COUNT(*) 
        FROM dim_date 
        GROUP BY mlb_season_phase 
        ORDER BY COUNT(*) DESC
        """)
        
        print(f"   🏟️  MLB Season Phases:")
        for phase, count in mlb_phases:
            print(f"     {phase}: {count} days")
        
        # Sample recent dates
        print(f"   📋 Sample recent dates:")
        sample = db.fetch_results("""
        SELECT TOP 5 date_key, full_date, day_name, mlb_season_phase, is_weekend
        FROM dim_date 
        WHERE full_date >= GETDATE() - 10
        ORDER BY full_date
        """)
        
        for row in sample:
            date_key, full_date, day_name, phase, is_weekend = row
            weekend_marker = " (Weekend)" if is_weekend else ""
            print(f"     {date_key}: {full_date} ({day_name}) - {phase}{weekend_marker}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying date dimension: {e}")
        return False
    finally:
        db.disconnect()

if __name__ == "__main__":
    print("📅 MLB DATA PIPELINE - DATE DIMENSION SETUP")
    print("=" * 70)
    
    success_count = 0
    
    # Step 1: Create table
    if create_date_dimension_table():
        success_count += 1
    
    # Step 2: Populate data (2020-2030 covers MLB historical and future data)
    if populate_date_dimension(2020, 2030):
        success_count += 1
    
    # Step 3: Verify
    if verify_date_dimension():
        success_count += 1
    
    print(f"\n📊 SUMMARY:")
    print(f"Successfully completed: {success_count}/3 steps")
    
    if success_count == 3:
        print(f"\n🎯 Date dimension table created successfully!")
        print(f"✅ dim_date table ready for analytics and reporting")
        print(f"✅ Includes MLB-specific season phases and business logic")
        print(f"✅ Optimized with indexes for performance")
    else:
        print(f"\n⚠️  Partial success: {success_count}/3 steps completed")
        sys.exit(1)
