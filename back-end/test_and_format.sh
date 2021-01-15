# Must run in python env
python -m unittest discover
python -m black *.py
python -m tools/black *.py
python -m tests/black *.py
python -m scripts/black *.py
python -m scripts/scrapers/black *.py