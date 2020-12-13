create table if not exists records (
    expert_id int,  -- foreign key to expert
    score int,
    primary key (expert_id)
);

CREATE VIEW `expert_with_records` AS
select  x.*, y.score
from    expert x
inner join
        records y
on      x.expert_id = y.expert_id
order by
        y.score desc;
