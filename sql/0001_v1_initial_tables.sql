create table if not exists game (
    game_date int,
    season int,
    week int,
    play_status varchar(255),
    home_team_id int,
    away_team_id int,
    mutual_location bool,
    home_score int,
    away_score int,
    primary key (game_date, home_team_id)
);

create table if not exists team (
    team_id int,
    short_name varchar(255),
    primary key (team_id)
);

create table if not exists team_cw (
    team_text varchar(255),
    team_id int,
    primary key (team_text)
    -- foreign key (team_id) references team(team_id)
);

CREATE VIEW `games_with_team_names` AS
select      x.*,
            home.short_name as home_team_name,
            away.short_name as away_team_name
from        game x
inner join  team home
on          x.home_team_id=home.team_id
inner join  team away
on          x.away_team_id=away.team_id;

insert into team
values  (1, "Packers"),
        (2, "Bears"),
        (3, "Lions"),
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
