drop table odd;
create table if not exists odd (
    game_date int,
    home_team_id int,
    pull_date int,
    pull_hour int,
    odds_type varchar(255), -- enum {"H2H", "SPREAD"},
    odds_home float,
    odds_away float,
    primary key (game_date, home_team_id, pull_date, pull_hour, odds_type)
);
