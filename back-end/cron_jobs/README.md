The pattern we're following for scripts in this folder is thusly:

Each script should be self-contained to run without flags.

We then build from back-end top-level (because this is how our folders are
linked) using pyinstaller run manually from command line.  (Make sure you run
this from the right environment.)

```
pyinstaller --onefile cron_jobs/fn.py
```

We then schedule a crontab job to run the script from the dist folder set to the
frequency specified in the header comment of the original script.
