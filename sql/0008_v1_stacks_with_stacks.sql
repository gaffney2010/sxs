CREATE VIEW stacks_with_stacks AS
    SELECT 
        x.expert_id AS expert_id,
        x.affiliate AS affiliate,
        x.prediction_date AS prediction_date,
        x.fetched_date AS fetched_date,
        x.game_date AS game_date,
        x.home_team_id AS home_team_id,
        x.away_team_id AS away_team_id,
        x.predicted_winner_id AS predicted_winner_id,
        x.predicted_winner_id_with_spread AS predicted_winner_id_with_spread,
        x.spread_favorite AS spread_favorite,
        x.spread_amt AS spread_amt,
        x.body AS body,
        x.link AS link,
        x.exclude AS exclude,
        y.expert_text AS expert_name,
        pred.short_name AS predicted_winner_name
    FROM
        ((stack x
        JOIN expert y ON (x.expert_id = y.expert_id))
        JOIN team pred ON (x.predicted_winner_id_with_spread = pred.team_id));