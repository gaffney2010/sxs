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
on          x.away_team_id=away.team_id;

# Some of these don't really work with sqlite.  IDK what to do?
drop view stacks_with_stacks_with_stacks;
create view stacks_with_stacks_with_stacks as
select 		*
from		(
			select		exp.expert_text as expert_name,
						x.game_key,
						x.expert_id,
						x.affiliate,
						x.link,
						pred.short_name as predicted_winner_name,
						x.predicted_winner_id,
						x.money_line,
						rec.score,
						rec.at_date,
						row_number() over (partition by expert_id, game_key order by at_date desc) rn
			from		stack x
			inner join 	expert exp
					on 	x.expert_id = exp.expert_id
			inner join  team pred
					on  x.predicted_winner_id = pred.team_id
			inner join	game g
					on  x.game_key = g.game_key
			inner join 	records rec
					on  rec.expert_id = exp.expert_id
					and	rec.at_date < g.game_date
			) t
where		rn = 1;

drop view expert_details;
CREATE VIEW expert_details AS
select  	x.expert_id,
	        z.game_date,
	        home.short_name AS home_team_name,
	        away.short_name AS away_team_name,
	        z.home_score,
	        z.away_score,
	        x.link,
	        x.predicted_winner_id,
	        x.money_line,
	        pred.short_name AS predicted_winner_name
from		stack x
inner join  expert y
		ON 	x.expert_id = y.expert_id
inner join  team pred
		ON  x.predicted_winner_id = pred.team_id
inner join  game z
  		on  x.game_key=z.game_key
inner join  team home
		on 	z.home_team_id = home.team_id
inner join  team away
		on  z.away_team_id = away.team_id;

drop view expert_with_records;
CREATE VIEW expert_with_records AS
select		*
from		(
			select  	x.*,
						y.score,
						row_number() over (partition by x.expert_id order by y.at_date desc) as rn
			from    	expert x
			inner join  records y
					on  x.expert_id = y.expert_id
			) t
where		rn = 1;
