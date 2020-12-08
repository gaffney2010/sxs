CREATE VIEW `stack_with_outcomes` AS
select  	x.*,
			y.home_score,
            y.away_score
from    	stack x
inner join	game y
on      	x.game_date = y.game_date
		and x.home_team_id = y.home_team_id
where		y.home_score <> y.away_score -- eliminate ties
		and	y.play_status = 3
        and x.exclude = 0;