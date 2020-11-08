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

expert table
------------

Columns:
  * expert_id
  * short_name

stack table
-----------

There are three ways that we may get a stack:

  1. We may get a prediction of who will win.
  2. We may get a prediction of who will beat the spread.
  3. We may get a prediction of the score.

Of course, spread here is the spread provided by the predictor.

Columns:

  * expert_id
  * prediction_date
  * fetched_date
  * game_date
  * team_1
  * score_1 - scenario 3 only
  * team_2
  * score_2 - scenario 3 only
  * predicted_winner - scenario 1 and 3
  * predicted_winner_with_spread - scenario 2 and later 3 
  * spread_favorite - scenario 2
  * spread_amt - scenario 2
