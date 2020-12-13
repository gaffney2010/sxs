-- drop table expert;
create table if not exists odd (
    game_id int, -- foreign key to game
    game_date int,
    hour int,
    odd_type varchar(255), -- enum {"H2H", "SPREAD"}
    avg float,
    primary key (game_id, game_date, hour)
);
