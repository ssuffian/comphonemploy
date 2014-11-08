import yaml
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Column, Table
from sqlalchemy import Integer, String, DateTime, Boolean

with open('../config.yaml') as f:
    cf = yaml.safe_load(f)

engine = create_engine('postgresql://'+cf['postgres_username']+':'+
                       cf['postgres_password']+'@localhost/'+cf['postgres_db'])
metadata = MetaData(bind=engine)
posts_table = Table('posts', metadata,
                    Column('id', String, primary_key=True),
                    Column('address', String(200)),
                    Column('body', String(10000)),
                    Column('date_posted', DateTime),
                    Column('pay',String(200)),
                    Column('phone_number',String(100)),
                    Column('new',Boolean),
                    Column('text',String(140)),
                    Column('search_criteria',String(140)),
                    )
users_table = Table('users', metadata,
                        Column('password', String), 
                        Column('email_address', String),
                        Column('phone_number', String, primary_key=True,nullable=False),
                        Column('search_criteria', String, nullable=False), 
                        )
# create or drops tables in database

metadata.drop_all()
metadata.create_all()
