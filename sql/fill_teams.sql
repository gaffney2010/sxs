-- drop table u995391212_stackql.team;
create table if not exists u995391212_stackql.team (
    team_id int,
    short_name varchar(255),
    primary key (team_id)
);

insert into u995391212_stackql.team
values 	(1, "Packers"),
		(2, "Bears"),
        (3, "Packers"),
        (4, "Vikings"),
        (5, "Cowboys"),
        (6, "Giants"),
        (7, "Eagles"),
        (8, "Washington"),
        (9, "Falcons"),
        (10, "Panthers"),
        (11, "Saints"),
        (12, "Buccaneers"),
        (13, "Cardinals"),
        (14, "Rams"),
        (15, "49ers"),
        (16, "Seahawks"),
        (17, "Ravens"),
        (18, "Bengals"),
        (19, "Browns"),
        (20, "Steelers"),
        (21, "Bills"),
        (22, "Dolphins"),
        (23, "Patriots"),
        (24, "Jets"),
        (25, "Texans"),
        (26, "Colts"),
        (27, "Jaguars"),
        (28, "Titans"),
        (29, "Broncos"),
        (30, "Chiefs"),
        (31, "Raiders"),
        (32, "Chargers");
        