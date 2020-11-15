-- drop table expert;
create table if not exists expert (
    expert_id varchar(255),
    expert_type varchar(255),  -- enum "UNKNOWN", HUMAN", "MODEL"
    expert_text varchar(255),
    primary key (expert_id)
);

-- drop table expert_cw;
create table if not exists expert_cw (
    expert_text varchar(255),
    expert_id varchar(255)
);

-- drop table stack;
create table if not exists stack (
    expert_id varchar(255),
    affiliate varchar(255),
    prediction_date int,
    fetched_date int,
    game_date int,
    home_team_id int,
    away_team_id int,
    predicted_winner_id int,
    predicted_winner_id_with_spread int,
    spread_favorite int,
    spread_amt float,
    body varchar(255),
    link varchar(255),
    exclude boolean,
    primary key (expert_id, game_date, home_team_id)
);
