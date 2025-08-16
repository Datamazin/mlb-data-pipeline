-- MLB season phase analysis
SELECT d.mlb_season_phase, AVG(home_score + away_score) as avg_total_runs
FROM dim_date d
JOIN dbo.games g ON CAST(g.official_date AS DATE) = d.full_date
WHERE d.year = 2025
GROUP BY d.mlb_season_phase;