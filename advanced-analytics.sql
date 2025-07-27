-- =====================================================
-- ADVANCED MLB ANALYTICS DAX MEASURES
-- =====================================================
-- Advanced DAX measures for deeper baseball analytics

-- =====================================================
-- ADVANCED BATTING METRICS
-- =====================================================

-- Slugging Percentage (requires additional data - using simplified version)
Slugging Percentage Estimate = 
VAR TotalHits = SUM(FACT_BOXSCORE[hits])
VAR TotalAtBats = SUM(FACT_BOXSCORE[at_bats])
-- Simplified: assuming 1.5x multiplier for estimated extra base hits
VAR EstimatedTotalBases = TotalHits * 1.5
RETURN 
    IF(TotalAtBats > 0,
       DIVIDE(EstimatedTotalBases, TotalAtBats, 0),
       BLANK())

-- OPS (On-base Plus Slugging)
OPS = 
[On Base Percentage] + [Slugging Percentage Estimate]

-- Plate Discipline Score
Plate Discipline Score = 
VAR WalkRate = [Walk Rate]
VAR StrikeoutRate = [Strikeout Rate]
RETURN 
    (WalkRate * 100) - (StrikeoutRate * 100)

-- =====================================================
-- SITUATIONAL PERFORMANCE
-- =====================================================

-- Clutch Performance (RBI efficiency)
Clutch Performance = 
VAR TotalRBI = SUM(FACT_BOXSCORE[rbi])
VAR TotalHits = SUM(FACT_BOXSCORE[hits])
RETURN 
    IF(TotalHits > 0,
       DIVIDE(TotalRBI, TotalHits, 0),
       BLANK())

-- Run Production Rate
Run Production Rate = 
VAR TotalRuns = SUM(FACT_BOXSCORE[runs])
VAR TotalRBI = SUM(FACT_BOXSCORE[rbi])
VAR TotalAtBats = SUM(FACT_BOXSCORE[at_bats])
RETURN 
    IF(TotalAtBats > 0,
       DIVIDE(TotalRuns + TotalRBI, TotalAtBats, 0),
       BLANK())

-- =====================================================
-- TEAM COMPARISON METRICS
-- =====================================================

-- Team vs League Comparison Table
Team Performance vs League = 
VAR TeamStats = 
    "TEAM vs LEAGUE COMPARISON" & UNICHAR(10) &
    "=========================" & UNICHAR(10) &
    "Batting Avg: " & FORMAT([Team Batting Average], "0.000") & 
    " (League: " & FORMAT(CALCULATE([Batting Average], ALL(DIM_TEAMS)), "0.000") & ")" & UNICHAR(10) &
    "Runs: " & FORMAT([Team Total Runs], "#,0") & 
    " (Rank: #" & [Team Runs Rank] & ")" & UNICHAR(10) &
    "RBI: " & FORMAT([Team Total RBI], "#,0") & UNICHAR(10) &
    "Strikeout Rate: " & FORMAT([Team Strikeout Rate], "0.0%")
RETURN TeamStats

-- Offensive Efficiency Rating
Offensive Efficiency = 
VAR RunsPerHit = DIVIDE([Total Runs], [Total Hits], 0)
VAR RBIPerHit = DIVIDE([Total RBI], [Total Hits], 0)
VAR WalkToStrikeoutRatio = DIVIDE([Total Walks], [Total Strikeouts], 0)
RETURN 
    (RunsPerHit * 40) + (RBIPerHit * 40) + (WalkToStrikeoutRatio * 20)

-- =====================================================
-- ROLLING AVERAGES AND TRENDS
-- =====================================================

-- 10-Game Rolling Batting Average
Rolling 10 Game BA = 
VAR Last10Games = 
    TOPN(10, 
         CALCULATETABLE(
             VALUES(FACT_BOXSCORE[game_id]),
             ALLEXCEPT(FACT_BOXSCORE, DIM_PLAYERS[player_id])
         ),
         RELATED(DIM_DATE[full_date]),
         DESC)
RETURN 
    CALCULATE(
        [Batting Average],
        KEEPFILTERS(FACT_BOXSCORE[game_id] IN Last10Games)
    )

-- Monthly Trend Indicator
Monthly Trend = 
VAR CurrentMonth = [Batting Average]
VAR PreviousMonth = CALCULATE(
    [Batting Average],
    DATEADD(DIM_DATE[full_date], -1, MONTH)
)
VAR TrendDirection = CurrentMonth - PreviousMonth
RETURN 
    IF(NOT ISBLANK(TrendDirection),
       IF(TrendDirection > 0.010, "📈 Rising",
          IF(TrendDirection < -0.010, "📉 Falling", "➡️ Stable")),
       "📊 N/A")

-- =====================================================
-- HOME vs AWAY PERFORMANCE
-- =====================================================

-- Home Game Performance
Home Performance = 
CALCULATE(
    [Batting Average],
    USERELATIONSHIP(DIM_TEAMS[team_id], FACT_GAMES[home_team_id])
)

-- Away Game Performance  
Away Performance = 
CALCULATE(
    [Batting Average],
    USERELATIONSHIP(DIM_TEAMS[team_id], FACT_GAMES[away_team_id])
)

-- Home vs Away Differential
Home Away Differential = 
[Home Performance] - [Away Performance]

-- =====================================================
-- MILESTONE TRACKING
-- =====================================================

-- Games to Next Milestone
Games to 100 Hits = 
VAR CurrentHits = [Total Hits]
VAR HitsPerGame = DIVIDE([Total Hits], [Player Games Played], 0)
RETURN 
    IF(CurrentHits < 100 AND HitsPerGame > 0,
       CEILING(DIVIDE(100 - CurrentHits, HitsPerGame, 0), 1),
       BLANK())

-- Season Projection
Season Hit Projection = 
VAR HitsPerGame = DIVIDE([Total Hits], [Player Games Played], 0)
VAR EstimatedSeasonGames = 162 -- Full season
RETURN 
    IF(HitsPerGame > 0,
       HitsPerGame * EstimatedSeasonGames,
       BLANK())

-- =====================================================
-- PERFORMANCE CATEGORIES
-- =====================================================

-- Player Category Classification
Player Category = 
VAR BattingAvg = [Batting Average]
VAR TotalHits = [Total Hits]
VAR Games = [Player Games Played]
RETURN 
    SWITCH(
        TRUE(),
        BattingAvg >= 0.300 AND TotalHits >= 150, "⭐ All-Star",
        BattingAvg >= 0.275 AND TotalHits >= 100, "🌟 Above Average",
        BattingAvg >= 0.250 AND Games >= 50, "📊 Average",
        BattingAvg >= 0.200, "📉 Below Average",
        "🚨 Struggling"
    )

-- Team Strength Rating
Team Strength = 
VAR TeamAvg = [Team Batting Average]
VAR TeamRuns = [Team Total Runs]
VAR GamesPlayed = CALCULATE(DISTINCTCOUNT(FACT_GAMES[game_id]))
VAR RunsPerGame = DIVIDE(TeamRuns, GamesPlayed, 0)
RETURN 
    SWITCH(
        TRUE(),
        TeamAvg >= 0.280 AND RunsPerGame >= 5.5, "🏆 Elite",
        TeamAvg >= 0.260 AND RunsPerGame >= 4.8, "💪 Strong", 
        TeamAvg >= 0.240 AND RunsPerGame >= 4.2, "⚖️ Average",
        TeamAvg >= 0.220, "📉 Weak",
        "🆘 Poor"
    )

-- =====================================================
-- CONSISTENCY METRICS
-- =====================================================

-- Batting Average Standard Deviation (Game-by-Game)
BA Consistency = 
VAR GameByGameBA = 
    ADDCOLUMNS(
        SUMMARIZE(FACT_BOXSCORE, FACT_BOXSCORE[game_id]),
        "GameBA", DIVIDE(
            CALCULATE(SUM(FACT_BOXSCORE[hits])),
            CALCULATE(SUM(FACT_BOXSCORE[at_bats]))
        )
    )
VAR Variance = 
    SUMX(GameByGameBA, 
         POWER([GameBA] - [Batting Average], 2)
    ) / COUNTROWS(GameByGameBA)
RETURN 
    SQRT(Variance)

-- Hot Streak Detection
Current Streak = 
VAR Last5GamesHits = 
    SUMX(
        TOPN(5, 
             RELATEDTABLE(FACT_BOXSCORE),
             FACT_BOXSCORE[created_at],
             DESC),
        FACT_BOXSCORE[hits]
    )
VAR Last5GamesAB = 
    SUMX(
        TOPN(5, 
             RELATEDTABLE(FACT_BOXSCORE),
             FACT_BOXSCORE[created_at],
             DESC),
        FACT_BOXSCORE[at_bats]
    )
VAR Recent5GameBA = DIVIDE(Last5GamesHits, Last5GamesAB, 0)
VAR SeasonBA = [Batting Average]
RETURN 
    IF(Recent5GameBA > SeasonBA * 1.2, "🔥 Hot Streak",
       IF(Recent5GameBA < SeasonBA * 0.8, "🧊 Cold Streak", 
          "📊 Normal"))

-- =====================================================
-- MULTI-DIMENSIONAL ANALYSIS
-- =====================================================

-- Player Value Score (Composite Metric)
Player Value Score = 
VAR BattingComponent = [Batting Average] * 40
VAR PowerComponent = [Run Production Rate] * 30
VAR DisciplineComponent = [Plate Discipline Score] * 0.2
VAR ConsistencyComponent = (1 - [BA Consistency]) * 10
RETURN 
    BattingComponent + PowerComponent + DisciplineComponent + ConsistencyComponent

-- Team Chemistry Index
Team Chemistry Index = 
VAR TeamRBI = [Team Total RBI]
VAR TeamRuns = [Team Total Runs]
VAR ExpectedRuns = TeamRBI * 1.1  -- Expected multiplier
VAR Chemistry = DIVIDE(TeamRuns, ExpectedRuns, 0)
RETURN 
    IF(Chemistry > 1.1, "🤝 Excellent",
       IF(Chemistry > 0.95, "👍 Good",
          IF(Chemistry > 0.85, "📊 Average", "📉 Poor")))

-- =====================================================
-- EXPORT SUMMARY FOR REPORTS
-- =====================================================

-- Executive Summary
Executive Summary = 
VAR TopPlayer = 
    MAXX(
        TOPN(1, ALL(DIM_PLAYERS), [Total Hits], DESC),
        DIM_PLAYERS[player_name]
    )
VAR TopTeam = 
    MAXX(
        TOPN(1, ALL(DIM_TEAMS), [Team Total Runs], DESC),
        DIM_TEAMS[team_name]
    )
RETURN 
    "SEASON EXECUTIVE SUMMARY" & UNICHAR(10) &
    "=======================" & UNICHAR(10) &
    "Top Hitter: " & TopPlayer & UNICHAR(10) &
    "Top Offensive Team: " & TopTeam & UNICHAR(10) &
    "League Batting Avg: " & FORMAT(CALCULATE([Batting Average], ALL()), "0.000") & UNICHAR(10) &
    "Total Games Analyzed: " & FORMAT(DISTINCTCOUNT(FACT_BOXSCORE[game_id]), "#,0")

-- =====================================================
-- END ADVANCED MEASURES
-- =====================================================
