SELECT 
        p.player_name,
        COUNT(DISTINCT b.game_id) as regular_season_games,
        COUNT(b.game_id) as total_plate_appearances
    FROM boxscore b
    INNER JOIN players p ON b.player_id = p.player_id
    INNER JOIN games g ON b.game_id = g.game_id
    WHERE g.game_type = 'R'
    GROUP BY p.player_name, p.player_id
    ORDER BY regular_season_games DESC, total_plate_appearances DESC
