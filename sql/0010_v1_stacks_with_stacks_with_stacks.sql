create view stacks_with_stacks_with_stacks as
select x.*, y.score
from stacks_with_stacks x
inner join records y
on x.expert_id=y.expert_id
