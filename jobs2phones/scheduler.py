import jobs2phones as j2p
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

with open('../config.yaml') as f:
    cf = yaml.safe_load(f)

def execute_compemploy():
    search_term='warehouse&20philadelphia'
    search_type='lab'
    j2p.read_rss_and_load(search_type,search_term,cf['data_dir'])
    df = j2p.create_df(cf['data_dir'],search_term)
    df_valid = j2p.get_valid_texts(df)
    Session = j2p.bind_to_database(cf['postgres_username'],cf['postgres_password'],cf['postgres_db'])
    j2p.load_data(Session,df_valid)
    j2p.send_from_database(Session)

scheduler = BlockingScheduler()
scheduler.add_job(j2p.execute_compemploy,'interval',hours=1)
try:
        scheduler.start()
except (KeyboardInterrupt, SystemExit):
        pass
