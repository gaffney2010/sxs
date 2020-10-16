game table
----------

If at a mutual location, then the teams are placed randomly between home and away.

Home and away team ID will be foreign keys.

Columns:

  * game_id
  * play_status (enum) - UPCOMING, LIVE, PAST
  * home_team_id
  * away_team_id
  * mutual_location (bool)
  * home_score
  * away_score
  * ot (int)

team table
----------

Columns:

  * team_id
  * short_name