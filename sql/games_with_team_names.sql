CREATE VIEW `games_with_team_names` AS
select		x.*,
			home.short_name as home_team_name,
			away.short_name as away_team_name
from		u995391212_stackql.game x
inner join	team home
on			x.home_team_id=home.team_id
inner join	team away
on			x.away_team_id=away.team_id;
