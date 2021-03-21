alter table swsws_table
add column consensus varchar(255);


create table if not exists consensus (
	game_key varchar(255),
	consensus_id int,
	primary key (game_key)
);


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
						row_number() over (partition by expert_id, game_key order by at_date desc) rn,
						con.consensus_id
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
			left join	consensus con
					on	x.game_key = con.game_key
			) t
where		rn = 1;
