#!/bin/bash
# Need to run these in environment
# TODO(#18): Create a binary for copy_db.
python copy_db.py --version=v1 --table=game
python copy_db.py --version=v1 --table=team
python copy_db.py --version=v1 --table=team_cw
