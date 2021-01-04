create table if not exists game (
    game_key varchar(255), -- YYYYMMDD#x(id)
    game_date int,
    play_status varchar(255), -- UPCOMING, LIVE, PAST
    home_team_id int,  -- foreign key
    away_team_id int,  -- foreign key
    home_score int,
    away_score int,
    primary key (game_key)
);

create table if not exists team (
    team_id int,
    short_name varchar(255),
    primary key (team_id)
);

insert into team
values  (1, "Bruins"),
        (2, "Sabres"),
        (3, "Red Wings"),
        (4, "Panthers"),
        (5, "Canadiens"),
        (6, "Senators"),
        (7, "Lightning"),
        (8, "Maple Leafs"),
        (9, "Hurricanes"),
        (10, "Blue Jackets"),
        (11, "Devils"),
        (12, "Islanders"),
        (13, "Rangers"),
        (14, "Flyers"),
        (15, "Penguins"),
        (16, "Capitals"),
        (17, "Blackhawks"),
        (18, "Avalanche"),
        (19, "Stars"),
        (20, "Wild"),
        (21, "Predators"),
        (22, "Blues"),
        (23, "Jets"),
        (24, "Ducks"),
        (25, "Coyotes"),
        (26, "Flames"),
        (27, "Oilers"),
        (28, "Kings"),
        (29, "Sharks"),
        (30, "Canucks"),
        (31, "Golden Knights");

create table if not exists team_cw (
    team_text varchar(255),
    team_id int,  -- foreign key
    primary key (team_text)
);

create table if not exists expert (
    expert_id int,
    expert_type varchar(255),  -- enum "UNKNOWN", HUMAN", "MODEL"
    expert_text varchar(255),
    primary key (expert_id)
);

create table if not exists expert_cw (
    expert_text varchar(255),
    expert_id int, -- foreign key
    primary key (expert_text)
);

create table if not exists stack (
    expert_id int, -- foreign key
    affiliate varchar(255),
    game_key varchar(255), -- foreign key
    predicted_winner_id int,
    money_line int,
    body varchar(255),
    link varchar(255),
    prediction_date int,
    fetched_date int,
    exclude boolean,
    primary key (expert_id, game_key)
);

create table if not exists odd (
    game_key varchar(255), -- foreign key
    pull_date int,
    pull_hour int,
    team_1 int, -- foreign key
    money_line_1 int,
    team_2 int,
    money_line_2 int,
    primary key (game_key)
);

create table if not exists records (
    expert_id int,  -- foreign key
    score int,
    primary key (expert_id)
);
