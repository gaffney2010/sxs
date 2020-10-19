drop table u995391212_stackql.game;
create table if not exists u995391212_stackql.game (
    game_date int,
    season int,
    week int,
    play_status enum('UPCOMING', 'LIVE', 'PAST'),
    home_team_id int,
    away_team_id int,
    mutual_location bool,
    home_score int,
    away_score int,
    primary key (game_date, home_team_id)
);

-- insert into u995391212_stackql.game
-- values 	(1, 'PAST', 1, 2, false, 20, 10, 0),
-- 		(2, 'PAST', 1, 3, false, 20, 10, 0),
-- 		(3, 'PAST', 1, 3, false, 20, 10, 0);
