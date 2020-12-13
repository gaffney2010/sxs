CREATE VIEW expert_details AS
    SELECT 
        x.expert_id AS expert_id,
        x.game_date AS game_date,
        home.short_name AS home_team_name,
        away.short_name AS away_team_name,
        z.home_score,
        z.away_score,
        x.spread_favorite AS spread_favorite,
        x.spread_amt AS spread_amt,
        x.link AS link,
        x.predicted_winner_id_with_spread,
        pred.short_name AS predicted_winner_name
    FROM stack x
        inner join expert y ON x.expert_id = y.expert_id
        inner join team pred ON x.predicted_winner_id_with_spread = pred.team_id
        inner join team home on x.home_team_id = home.team_id
        inner join team away on x.away_team_id = away.team_id
        inner join game z on x.home_team_id=z.home_team_id and x.game_date=z.game_date;
