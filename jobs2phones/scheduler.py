import execute
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()
scheduler.add_job(execute.execute_compemploy,'interval',hours=1)
try:
        scheduler.start()
except (KeyboardInterrupt, SystemExit):
        pass
