import load
import yaml

with open('../config.yaml') as f:
        cf = yaml.safe_load(f)
search_term='warehouse&20philadelphia'

Session = load.bind_to_database(cf['postgres_username'],
        cf['postgres_password'],cf['postgres_db'])
load.insert_user(Session,'',cf['toaddrs_demo'],'pword',search_term)
