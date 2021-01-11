# Make sure you're in the right env
pyinstaller --onefile cron_jobs/pull_nhl.py
pyinstaller --onefile cron_jobs/pull_odds.py
pyinstaller --onefile cron_jobs/migrate_db.py