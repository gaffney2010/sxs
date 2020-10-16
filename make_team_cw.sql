-- drop table u995391212_stackql.team_cw;
create table if not exists u995391212_stackql.team_cw (
	team_text varchar(255),
    team_id int,
    foreign key (team_id) references u995391212_stackql.team(team_id)
);
