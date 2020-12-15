# Make sure you're in the right env
pyinstaller --onefile cron_jobs/backup_local_db.py
pyinstaller --onefile cron_jobs/game_scrapper.py
pyinstaller --onefile cron_jobs/odds_scrapper.py
pyinstaller --onefile cron_jobs/run_compute_records.py
pyinstaller --onefile cron_jobs/stack_scrapper.py