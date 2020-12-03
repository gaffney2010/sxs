-- Earlier expert table had expert_id as a varchar, and we want it to be int

-- drop table expert_copy;

create table expert_copy as
select cast(expert_id as int) as expert_id, expert_type, expert_text from expert;

drop table expert;

create table expert (
    expert_id int,
    expert_type varchar(255),  -- enum "UNKNOWN", HUMAN", "MODEL"
    expert_text varchar(255),
    primary key (expert_id)
);
