# Make sure you're in the right env
pyinstaller --onefile cron_jobs/pull_nhl.py
pyinstaller --onefile cron_jobs/pull_odds.py
pyinstaller --onefile cron_jobs/migrate_db.py
pyinstaller --onefile cron_jobs/scrape_a_few.py
pyinstaller --onefile cron_jobs/compute_records.py
pyinstaller --onefile cron_jobs/compute_consensus.py
pyinstaller --onefile cron_jobs/cache_reaper.py
pyinstaller --onefile cron_jobs/backup_db.py