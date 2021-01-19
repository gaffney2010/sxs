drop view games_with_team_names;
CREATE VIEW games_with_team_names AS
select      x.game_key,
			x.game_date,
			x.home_score,
			x.away_score,
            home.short_name as home_team_name,
            away.short_name as away_team_name,
            x.play_status
from        game x
inner join  team home
on          x.home_team_id=home.team_id
inner join  team away
on          x.away_team_id=away.team_id
 -- Only list games with at least one stack.
inner join  (select distinct game_key from stack) stacked_games
on			x.game_key=stacked_games.game_key;
