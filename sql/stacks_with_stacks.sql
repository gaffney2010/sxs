CREATE VIEW `stacks_with_stacks` AS
select		x.*,
			y.expert_text as expert_name,
            pred.short_name as predicted_winner_name
from		stack x
inner join	expert y
on			x.expert_id=y.expert_id
inner join	team pred
on			x.predicted_winner_id_with_spread=pred.team_id;
