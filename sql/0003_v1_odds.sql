create table if not exists odd (
    game_date int,
    home_team_id int,
    odds_type varchar(255), -- enum {"H2H", "SPREAD"},
    odds_home float,
    odds_away float,
    primary key (game_date, home_team_id)
);
