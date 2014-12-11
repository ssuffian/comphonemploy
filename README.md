#This repository has been moved to https://github.com/jobs2phones/j2p so it can be an organization and have a github pages hosted website. This repository will no longer be updated.
#Computer To Phone To Employment

###The first goal of this code is to allow people to receive notifications from job posting sites that are filtered to those respondable by phone.
-  Read postings through RSS
-  Classify posting as respondable by phone or not
-  Filter posting to fit in a single text message
-  Send text message to appropriate users

###The second goal of this code is to allow people to receive forwarded emails to their phone in a filtered text.

-  Ingest forwarded email
-  Filter email to fit in single text message
-  Send text message

These two applications will allow those without smartphones to be able to get real-time notifications of events that previously required frequent checking of the computer. The hope is to make the playing ground between smartphone users and normal phone users more even when it comes to applying for jobs.

###Todo
-  Better filtering for phone numbers, pay, etc.
-  System for inputting users
-  Additional job sources
-  Include posts that are in-person (don't require email, but aren't necessarily phone)
-  Have not worked on any of the email to phone yet.

###Installation
sudo apt-get install python-pip python-dev postgresql-server-dev-all  
sudo pip install feedparser beautifulsoup4 pandas apscheduler pyyaml sqlalchemy psycopg2

Rename config-example.yaml config.yaml and change variables appropriately.  

###Postgres Setup

sudo apt-get install postgresql postgresql-contrib php5-pgsql  
sudo -u postgres psql postgres  
create database 'database';
create user 'user';  
\password 'user';  
grant all privileges on database 'database' to 'user';  
\q  
python setup_schema.py  

To log into postgres as this new user without also having to create a system user:
- sudo vim /etc/postgres/9.3/main/pg_hba.conf
- Change 'peer' to 'md5'
- sudo service postgresql restart

###Running The Program
scheduler.py is the python script that runs the program. There is a line in that python file with a parameter for setting how often to schedule the process.

'python scheduler.py &' will run the process in the background.
## Contact
Stephen Suffian
contact@jobs2phones.com
