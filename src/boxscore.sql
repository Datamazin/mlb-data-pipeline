/****** Script for SelectTopNRows command from SSMS  ******/
SELECT TOP (1000) [id]
      ,[game_id]
      ,[player_id]
      ,[team_id]
      ,[at_bats]
      ,[runs]
      ,[hits]
      ,[rbi]
      ,[walks]
      ,[strikeouts]
	  ,[doubles]
      ,[triples]
      ,[home_runs]
      ,[created_at]

  FROM [mlb_data].[dbo].[boxscore]
  