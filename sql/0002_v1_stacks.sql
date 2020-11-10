create table if not exists expert (
    expert_id varchar(255),
    name varchar(255),
    primary key (expert_id)
);

create table if not exists expert_cw (
    expert_text varchar(255),
    expert_id varchar(255)
);

create table if not exists stack (
    expert_id varchar(255),
    expert_type varchar(255),  -- enum "UNKNOWN", HUMAN", "MODEL"
    affiliate varchar(255),
    prediction_date int,
    fetched_date int,
    game_date int,
    home_team_id int,
    home_score int,
    away_team_id int,
    away_score int,
    predicted_winner_id int,
    predicted_winner_id_with_spread int,
    spread_favorite int,
    spread_amt int,
    body varchar(255),
    link varchar(255)
);
