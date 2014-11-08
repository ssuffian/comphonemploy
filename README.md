#Computer To Phone To Employment

###The first goal of this code is to allow people to receive notifications from job posting sites that are filtered to those respondable by phone.
- C1. Read postings through RSS
- C2. Classify posting as respondable by phone or not
- C3. Filter posting to fit in a single text message
- C4. Send text message to appropriate users

###The second goal of this code is to allow people to receive forwarded emails to their phone in a filtered text.

- E1. Ingest forwarded email
- E2. Filter email to fit in single text message
- E3. Send text message

These two applications will allow those without smartphones to be able to get real-time notifications of events that previously required frequent checking of the computer. The hope is to make the playing ground between smartphone users and normal phone users more even when it comes to applying for jobs.

###Todo
- C3 - Better filtering for phone numbers, pay, etc.
- C4 - System for inputting phone numbers for certain search terms
- E - Have not worked on any of the email to phone yet.

###Installation
sudo apt-get install python-pip  
sudo apt-get install python-dev  
sudo pip install feedparser  
sudo pip install beautifulsoup4  
sudo pip install pandas  
sudo pip install apscheduler  
sudo pip install pyyaml  
  
Rename config-example.yaml config.yaml and change variables appropriately.  

Setup
For postgres, run the following script to create the tables
(you must first create a username, password, and database and put it
in your yaml):
python setup_schema.py
