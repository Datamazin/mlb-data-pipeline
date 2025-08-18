-- =====================================================
-- STATISTICAL DISTRIBUTIONS & SABERMETRICS
-- =====================================================
-- Advanced statistical analysis for MLB data
-- Includes percentiles, correlations, and predictive metrics

-- =====================================================
-- PERCENTILE ANALYSIS
-- =====================================================

-- Player Performance Percentiles
WITH PlayerStats AS (
    SELECT 
        p.player_id,
        p.player_name,
        t.team_name,
        SUM(b.hits) as hits,
        SUM(b.at_bats) as at_bats,
        SUM(b.home_runs) as home_runs,
        SUM(b.rbi) as rbi,
        SUM(b.runs) as runs,
        SUM(b.walks) as walks,
        SUM(b.strikeouts) as strikeouts,
        
        -- Calculated rates
        CASE WHEN SUM(b.at_bats) > 0 
             THEN CAST(SUM(b.hits) AS DECIMAL(10,3)) / SUM(b.at_bats)
             ELSE 0 END as batting_avg,
             
        CASE WHEN SUM(b.at_bats) > 0 
             THEN CAST(SUM(b.home_runs) AS DECIMAL(10,3)) / SUM(b.at_bats)  
             ELSE 0 END as hr_rate,
             
        CASE WHEN (SUM(b.at_bats) + SUM(b.walks)) > 0
             THEN CAST(SUM(b.walks) AS DECIMAL(10,3)) / (SUM(b.at_bats) + SUM(b.walks))
             ELSE 0 END as walk_rate
             
    FROM boxscore b
    INNER JOIN players p ON b.player_id = p.player_id
    INNER JOIN teams t ON b.team_id = t.team_id
    INNER JOIN games g ON b.game_id = g.game_id
    WHERE g.game_date >= '2025-03-01'
    GROUP BY p.player_id, p.player_name, t.team_name
    HAVING SUM(b.at_bats) >= 100  -- Qualified players
)

-- Percentile Rankings
SELECT 
    player_name,
    team_name,
    FORMAT(batting_avg, 'N3') as BA,
    home_runs as HR,
    rbi as RBI,
    
    -- Percentile rankings
    PERCENT_RANK() OVER (ORDER BY batting_avg) * 100 as BA_percentile,
    PERCENT_RANK() OVER (ORDER BY home_runs) * 100 as HR_percentile,  
    PERCENT_RANK() OVER (ORDER BY rbi) * 100 as RBI_percentile,
    PERCENT_RANK() OVER (ORDER BY walk_rate) * 100 as BB_percentile,
    
    -- Overall performance score (weighted average of percentiles)
    (
        (PERCENT_RANK() OVER (ORDER BY batting_avg) * 30) +
        (PERCENT_RANK() OVER (ORDER BY home_runs) * 25) +
        (PERCENT_RANK() OVER (ORDER BY rbi) * 25) +
        (PERCENT_RANK() OVER (ORDER BY walk_rate) * 20)
    ) * 100 as overall_percentile_score
    
FROM PlayerStats
ORDER BY overall_percentile_score DESC;

-- =====================================================
-- DISTRIBUTION ANALYSIS
-- =====================================================

-- Batting Average Distribution (Histogram)
WITH BattingAvgBins AS (
    SELECT 
        CASE 
            WHEN batting_avg < 0.200 THEN 'Under .200'
            WHEN batting_avg < 0.250 THEN '.200-.249'  
            WHEN batting_avg < 0.275 THEN '.250-.274'
            WHEN batting_avg < 0.300 THEN '.275-.299'
            WHEN batting_avg < 0.325 THEN '.300-.324'
            WHEN batting_avg < 0.350 THEN '.325-.349'
            ELSE '.350+'
        END as avg_range,
        COUNT(*) as player_count
    FROM (
        SELECT 
            CAST(SUM(b.hits) AS DECIMAL(10,3)) / SUM(b.at_bats) as batting_avg
        FROM boxscore b
        INNER JOIN games g ON b.game_id = g.game_id  
        WHERE g.game_date >= '2025-03-01'
        GROUP BY b.player_id
        HAVING SUM(b.at_bats) >= 100
    ) player_avgs
    GROUP BY 
        CASE 
            WHEN batting_avg < 0.200 THEN 'Under .200'
            WHEN batting_avg < 0.250 THEN '.200-.249'
            WHEN batting_avg < 0.275 THEN '.250-.274' 
            WHEN batting_avg < 0.300 THEN '.275-.299'
            WHEN batting_avg < 0.325 THEN '.300-.324'
            WHEN batting_avg < 0.350 THEN '.325-.349'
            ELSE '.350+'
        END
)

-- Distribution Summary
SELECT 
    avg_range,
    player_count,
    FORMAT(CAST(player_count AS DECIMAL(10,2)) / SUM(player_count) OVER() * 100, 'N1') + '%' as percentage
FROM BattingAvgBins
ORDER BY 
    CASE avg_range
        WHEN 'Under .200' THEN 1
        WHEN '.200-.249' THEN 2
        WHEN '.250-.274' THEN 3
        WHEN '.275-.299' THEN 4  
        WHEN '.300-.324' THEN 5
        WHEN '.325-.349' THEN 6
        ELSE 7
    END;

-- =====================================================
-- CORRELATION ANALYSIS  
-- =====================================================

-- Runs vs RBI Correlation Analysis
WITH TeamOffensiveStats AS (
    SELECT 
        t.team_name,
        SUM(b.runs) as total_runs,
        SUM(b.rbi) as total_rbi,
        SUM(b.hits) as total_hits,
        SUM(b.home_runs) as total_hrs,
        SUM(b.walks) as total_walks
    FROM boxscore b
    INNER JOIN teams t ON b.team_id = t.team_id
    INNER JOIN games g ON b.game_id = g.game_id
    WHERE g.game_date >= '2025-03-01' 
    GROUP BY t.team_id, t.team_name
),

-- Calculate correlation statistics
CorrelationStats AS (
    SELECT 
        CAST(COUNT(*) AS BIGINT) as n,
        AVG(CAST(total_runs AS DECIMAL(15,2))) as avg_runs,
        AVG(CAST(total_rbi AS DECIMAL(15,2))) as avg_rbi,
        CAST(SUM(CAST(total_runs AS BIGINT) * CAST(total_rbi AS BIGINT)) AS DECIMAL(20,2)) as sum_runs_rbi,
        CAST(SUM(CAST(total_runs AS BIGINT) * CAST(total_runs AS BIGINT)) AS DECIMAL(20,2)) as sum_runs_sq,
        CAST(SUM(CAST(total_rbi AS BIGINT) * CAST(total_rbi AS BIGINT)) AS DECIMAL(20,2)) as sum_rbi_sq,
        CAST(SUM(total_runs) AS BIGINT) as sum_runs,
        CAST(SUM(total_rbi) AS BIGINT) as sum_rbi
    FROM TeamOffensiveStats
)

-- Correlation coefficient (Pearson)
SELECT 
    FORMAT(
        (CAST(n AS DECIMAL(20,2)) * sum_runs_rbi - CAST(sum_runs AS DECIMAL(20,2)) * CAST(sum_rbi AS DECIMAL(20,2))) /
        SQRT(
            (CAST(n AS DECIMAL(20,2)) * sum_runs_sq - POWER(CAST(sum_runs AS DECIMAL(20,2)), 2)) *
            (CAST(n AS DECIMAL(20,2)) * sum_rbi_sq - POWER(CAST(sum_rbi AS DECIMAL(20,2)), 2))
        ), 'N3'
    ) as runs_rbi_correlation
FROM CorrelationStats;

-- =====================================================
-- CONSISTENCY METRICS
-- =====================================================

-- Game-by-Game Performance Variance
WITH GamePerformance AS (
    SELECT 
        b.player_id,
        p.player_name,
        t.team_name,
        g.game_date,
        b.hits,
        b.at_bats,
        CASE WHEN b.at_bats > 0 THEN CAST(b.hits AS DECIMAL(10,3)) / b.at_bats ELSE NULL END as game_avg
    FROM boxscore b
    INNER JOIN players p ON b.player_id = p.player_id
    INNER JOIN teams t ON b.team_id = t.team_id  
    INNER JOIN games g ON b.game_id = g.game_id
    WHERE g.game_date >= '2025-03-01'
    AND b.at_bats > 0
),

PlayerConsistency AS (
    SELECT 
        player_id,
        player_name, 
        team_name,
        COUNT(*) as games_with_abs,
        AVG(game_avg) as avg_performance,
        STDEV(game_avg) as performance_stdev,
        MIN(game_avg) as worst_game,
        MAX(game_avg) as best_game
    FROM GamePerformance
    WHERE game_avg IS NOT NULL
    GROUP BY player_id, player_name, team_name
    HAVING COUNT(*) >= 10  -- At least 10 games with at-bats
)

-- Consistency Rankings
SELECT 
    player_name,
    team_name,
    games_with_abs,
    FORMAT(avg_performance, 'N3') as season_avg,
    FORMAT(performance_stdev, 'N3') as consistency_stdev,
    FORMAT(worst_game, 'N3') as worst_game,
    FORMAT(best_game, 'N3') as best_game,
    
    -- Consistency Score (lower standard deviation = more consistent)
    CASE 
        WHEN performance_stdev < 0.100 THEN '🎯 Very Consistent'
        WHEN performance_stdev < 0.150 THEN '📊 Consistent'  
        WHEN performance_stdev < 0.200 THEN '📈 Average Consistency'
        ELSE '🎢 Inconsistent'
    END as consistency_rating
    
FROM PlayerConsistency
WHERE avg_performance >= 0.250  -- Focus on decent performers
ORDER BY performance_stdev ASC;

-- =====================================================
-- LEVERAGE SITUATIONS
-- =====================================================

-- Performance in High-Leverage Situations (simplified)
-- Note: True leverage requires inning/score context which may need additional data

WITH HighLeverageApprox AS (
    SELECT 
        b.player_id,
        p.player_name,
        t.team_name,
        
        -- Approximate high-leverage as games with close final scores
        CASE WHEN ABS(
            COALESCE((SELECT SUM(runs) FROM boxscore WHERE game_id = b.game_id AND team_id = g.home_team_id), 0) -
            COALESCE((SELECT SUM(runs) FROM boxscore WHERE game_id = b.game_id AND team_id = g.away_team_id), 0)
        ) <= 3 THEN 'Close Game' ELSE 'Blowout' END as game_situation,
        
        b.hits,
        b.at_bats,
        b.rbi
        
    FROM boxscore b
    INNER JOIN players p ON b.player_id = p.player_id
    INNER JOIN teams t ON b.team_id = t.team_id
    INNER JOIN games g ON b.game_id = g.game_id
    WHERE g.game_date >= '2025-03-01'
    AND b.at_bats > 0
)

-- Close Game vs Blowout Performance
SELECT 
    player_name,
    team_name,
    
    -- Close game stats
    SUM(CASE WHEN game_situation = 'Close Game' THEN hits ELSE 0 END) as close_hits,
    SUM(CASE WHEN game_situation = 'Close Game' THEN at_bats ELSE 0 END) as close_abs,
    SUM(CASE WHEN game_situation = 'Close Game' THEN rbi ELSE 0 END) as close_rbi,
    
    -- Blowout stats
    SUM(CASE WHEN game_situation = 'Blowout' THEN hits ELSE 0 END) as blowout_hits,
    SUM(CASE WHEN game_situation = 'Blowout' THEN at_bats ELSE 0 END) as blowout_abs,
    
    -- Performance comparison
    CASE 
        WHEN SUM(CASE WHEN game_situation = 'Close Game' THEN at_bats ELSE 0 END) > 0
        THEN FORMAT(
            CAST(SUM(CASE WHEN game_situation = 'Close Game' THEN hits ELSE 0 END) AS DECIMAL(10,3)) /
            SUM(CASE WHEN game_situation = 'Close Game' THEN at_bats ELSE 0 END), 'N3'
        )
        ELSE 'N/A'
    END as close_game_avg,
    
    CASE 
        WHEN SUM(CASE WHEN game_situation = 'Blowout' THEN at_bats ELSE 0 END) > 0
        THEN FORMAT(
            CAST(SUM(CASE WHEN game_situation = 'Blowout' THEN hits ELSE 0 END) AS DECIMAL(10,3)) /
            SUM(CASE WHEN game_situation = 'Blowout' THEN at_bats ELSE 0 END), 'N3'
        )  
        ELSE 'N/A'
    END as blowout_avg
    
FROM HighLeverageApprox
GROUP BY player_id, player_name, team_name
HAVING SUM(at_bats) >= 50  -- Minimum plate appearances
ORDER BY close_rbi DESC;

-- =====================================================
-- PREDICTIVE METRICS
-- =====================================================

-- Rest vs Performance Analysis  
WITH GameSequence AS (
    SELECT 
        b.player_id,
        p.player_name,
        g.game_date,
        b.hits,
        b.at_bats,
        LAG(g.game_date) OVER (PARTITION BY b.player_id ORDER BY g.game_date) as prev_game_date,
        DATEDIFF(DAY, LAG(g.game_date) OVER (PARTITION BY b.player_id ORDER BY g.game_date), g.game_date) as days_rest
    FROM boxscore b
    INNER JOIN players p ON b.player_id = p.player_id
    INNER JOIN games g ON b.game_id = g.game_id  
    WHERE g.game_date >= '2025-03-01'
    AND b.at_bats > 0
),

RestAnalysis AS (
    SELECT 
        player_name,
        CASE 
            WHEN days_rest IS NULL THEN 'First Game'
            WHEN days_rest = 1 THEN 'No Rest' 
            WHEN days_rest = 2 THEN '1 Day Rest'
            WHEN days_rest <= 4 THEN '2-3 Days Rest'
            ELSE '4+ Days Rest'
        END as rest_category,
        COUNT(*) as games,
        SUM(hits) as total_hits,
        SUM(at_bats) as total_abs,
        FORMAT(CAST(SUM(hits) AS DECIMAL(10,3)) / SUM(at_bats), 'N3') as avg_performance
    FROM GameSequence
    WHERE days_rest IS NOT NULL
    GROUP BY 
        player_name,
        CASE 
            WHEN days_rest IS NULL THEN 'First Game'
            WHEN days_rest = 1 THEN 'No Rest'
            WHEN days_rest = 2 THEN '1 Day Rest' 
            WHEN days_rest <= 4 THEN '2-3 Days Rest'
            ELSE '4+ Days Rest'
        END
    HAVING SUM(at_bats) >= 20  -- Meaningful sample
)

-- Rest Impact Summary
SELECT 
    rest_category,
    COUNT(DISTINCT player_name) as players,
    SUM(games) as total_games,
    FORMAT(AVG(CAST(REPLACE(avg_performance, 'N/A', '0') AS DECIMAL(10,3))), 'N3') as avg_league_performance
FROM RestAnalysis  
WHERE avg_performance != 'N/A'
GROUP BY rest_category
ORDER BY 
    CASE rest_category
        WHEN 'No Rest' THEN 1
        WHEN '1 Day Rest' THEN 2
        WHEN '2-3 Days Rest' THEN 3
        WHEN '4+ Days Rest' THEN 4
        ELSE 5
    END;
