import load
import scrape
import parse
import send
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

with open('../config.yaml') as f:
    cf = yaml.safe_load(f)

def execute_compemploy():
    search_term='warehouse&20philadelphia'
    search_type='lab'
    scrape.read_rss_and_load(search_type,search_term,cf['data_dir'])
    df = parse.create_df(cf['data_dir'],search_term)
    df_valid = parse.get_valid_texts(df)
    Session = load.bind_to_database(cf['postgres_username']
            ,cf['postgres_password'],cf['postgres_db'])
    load.load_data(Session,df_valid)
    send.send_from_database(Session)
