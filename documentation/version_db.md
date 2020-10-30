Strategy
--------

Here is our strategy for DB versioning.

Today I have a version 1 games table, so I save this locally as a file (SQLite):
sxs/data/v1/games.db

This mirrors a remote table, named:
Games

I have scripts order by number, which build the table and copies data from local hard drive:
sxs/sql/0000_initial_tables.sql
sxs/sql/0001_copy_v1_games.sql

When I write to this table, I will write locally and remotely.  In pseudocode:

	* Set SQL_GAMES_VERSION = 1
	* Write to sxs/data/<SQL_GAMES_VERSION>/games.db
	* Write to Games (remote)

In order to update a table, I pause all other writes, then I make a version 2:
sxs/data/v2/games.db

Next I update my code to fill out the new table and change SQL_GAMES_VERSION = 2.

Finally I update the migration scripts:
sxs/sql/0000_initial_tables.sql
sxs/sql/0001_copy_v1_games.sql
sxs/sql/0002_update_games.sql
sxs/sql/0003_copy_v2_games.sql

Other notes
-----------

My automated scripts run on the current version of the code, because I have no CI.

I'll use a different script to backup data periodically to other sources.

I have no down migrations; I have to do full restores.