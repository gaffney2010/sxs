drop table records;

create table if not exists records (
    expert_id int,  -- foreign key
    at_date int,
    score int,
    primary key (expert_id, at_date)
);