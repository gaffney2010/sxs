game table
----------

If at a mutual location, then the teams are placed randomly between home and away.

Home and away team ID will be foreign keys.

Columns:

  * game_date - YYYYMMDD (+)
  * season - YYYY (year of start of season)
  * week
  * play_status (enum) - UPCOMING, LIVE, PAST
  * home_team_id (+)
  * away_team_id
  * mutual_location (bool)
  * home_score
  * away_score

(+) Part of the primary key

We also have a view, games_with_team_names, which has the same fields pluse home_team_name and away_team_name.

team table
----------

Columns:

  * team_id
  * short_name

team_cw table
---------------

This is a table that will let us look up a team_id, which is a foreign key

Columns:

  * team_text
  * team_id

