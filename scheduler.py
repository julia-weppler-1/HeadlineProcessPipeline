import logging
import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from main import run_pipeline

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Set the timezone to Eastern Time
    eastern = pytz.timezone("US/Eastern")
    scheduler = BlockingScheduler(timezone=eastern)
    
    # Schedule to run every Monday at midnight (00:00 ET)
    scheduler.add_job(run_pipeline, 'cron', day_of_week='mon', hour=0, minute=0)
    
    logging.info("Scheduler started; pipeline will run every Monday at midnight ET.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler stopped.")
