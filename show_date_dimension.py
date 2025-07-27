#!/usr/bin/env python3
"""
Show Date Dimension Table Details
Display the structure and sample data from the dim_date table.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.database.connection import DatabaseConnection

def show_date_dimension_details():
    """Display comprehensive details about the date dimension table."""
    
    db = DatabaseConnection()
    try:
        db.connect()
        
        print("📅 DATE DIMENSION TABLE DETAILS")
        print("=" * 70)
        
        # Table structure
        print("1. TABLE STRUCTURE:")
        structure = db.fetch_results("""
        SELECT 
            COLUMN_NAME,
            DATA_TYPE,
            IS_NULLABLE,
            CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'dim_date'
        ORDER BY ORDINAL_POSITION
        """)
        
        print("   Column Name                   Type           Nullable   Length")
        print("   " + "-" * 65)
        for col_name, data_type, nullable, max_length in structure:
            length_str = f"({max_length})" if max_length else ""
            print(f"   {col_name:<30} {data_type:<10}{length_str:<6} {nullable:<8}")
        
        # Sample data for current month
        print(f"\n2. SAMPLE DATA (Current Week):")
        sample = db.fetch_results("""
        SELECT TOP 10
            date_key,
            full_date,
            day_name,
            month_name,
            quarter_text,
            is_weekend,
            mlb_season_phase,
            days_from_today
        FROM dim_date 
        WHERE ABS(days_from_today) <= 7
        ORDER BY full_date
        """)
        
        print("   Date Key   Full Date   Day        Month      Quarter    Weekend  MLB Phase        Days From Today")
        print("   " + "-" * 95)
        for row in sample:
            date_key, full_date, day_name, month_name, quarter, is_weekend, mlb_phase, days_from_today = row
            weekend_marker = "Yes" if is_weekend else "No "
            print(f"   {date_key}  {full_date}  {day_name:<9}  {month_name:<9}  {quarter:<9}  {weekend_marker}      {mlb_phase:<15}  {days_from_today:>3}")
        
        # MLB season phase breakdown by year
        print(f"\n3. MLB SEASON PHASES BY YEAR:")
        mlb_breakdown = db.fetch_results("""
        SELECT 
            year,
            SUM(CASE WHEN mlb_season_phase = 'Spring Training' THEN 1 ELSE 0 END) as spring_training,
            SUM(CASE WHEN mlb_season_phase = 'Regular Season' THEN 1 ELSE 0 END) as regular_season,
            SUM(CASE WHEN mlb_season_phase = 'Playoffs' THEN 1 ELSE 0 END) as playoffs,
            SUM(CASE WHEN mlb_season_phase = 'Offseason' THEN 1 ELSE 0 END) as offseason
        FROM dim_date 
        WHERE year IN (2024, 2025, 2026)
        GROUP BY year
        ORDER BY year
        """)
        
        print("   Year   Spring Training   Regular Season   Playoffs   Offseason")
        print("   " + "-" * 65)
        for year, spring, regular, playoffs, offseason in mlb_breakdown:
            print(f"   {year}           {spring:>3}              {regular:>3}         {playoffs:>3}        {offseason:>3}")
        
        # Useful queries examples
        print(f"\n4. USEFUL ANALYTICS QUERIES:")
        print("   📊 Weekend games in current season:")
        weekend_games = db.fetch_results("""
        SELECT COUNT(*) as weekend_game_dates
        FROM dim_date d
        INNER JOIN dbo.games g ON CAST(g.official_date AS DATE) = d.full_date
        WHERE d.is_weekend = 1 AND d.year = 2025
        """)
        
        if weekend_games and weekend_games[0][0]:
            print(f"      {weekend_games[0][0]} game dates fall on weekends in 2025")
        
        print("   📊 Games by MLB season phase (2025):")
        phase_games = db.fetch_results("""
        SELECT 
            d.mlb_season_phase,
            COUNT(*) as game_count
        FROM dim_date d
        INNER JOIN dbo.games g ON CAST(g.official_date AS DATE) = d.full_date
        WHERE d.year = 2025
        GROUP BY d.mlb_season_phase
        ORDER BY game_count DESC
        """)
        
        for phase, count in phase_games:
            print(f"      {phase}: {count} games")
        
        print(f"\n5. INDEXES CREATED:")
        indexes = db.fetch_results("""
        SELECT 
            i.name as index_name,
            STRING_AGG(c.name, ', ') as columns
        FROM sys.indexes i
        JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
        JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
        JOIN sys.tables t ON i.object_id = t.object_id
        WHERE t.name = 'dim_date' AND i.type > 0
        GROUP BY i.name
        ORDER BY i.name
        """)
        
        for index_name, columns in indexes:
            print(f"   {index_name}: {columns}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error showing date dimension details: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.disconnect()

if __name__ == "__main__":
    show_date_dimension_details()
