import feedparser
import smtplib
import logging
from bs4 import BeautifulSoup
import re
import glob
import os
import pandas as pd
from urllib2 import urlopen,Request  # for Python 3: from urllib.request import urlopen
import difflib
import time
from apscheduler.schedulers.blocking import BlockingScheduler
import yaml
with open('../config.yaml') as f:
    cf = yaml.safe_load(f)

#search_term='cook&20philadelphia'
#search_type='fbh'
search_term='warehouse&20philadelphia'
search_type='lab'
directory = '../data/'+search_term+'/'
logging.basicConfig(filename='posting.log',level=logging.DEBUG)
to_address=cf['toaddrs_demo']
def load_craigs_page(entry):
    '''
    This method takes an entry from the RSS feed and loads
    sees whether or not that page has been stored. If the page
    has not yet been stored, it stores the page as html file.
    '''
    URL = entry['link']
    link_name = entry['id']
    exist_files = os.listdir(directory)

    duplicate = False
    for exist_file in exist_files:
        if exist_file in link_name:
            duplicate = True
    if not duplicate:
        headers = {'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; WindowsNT)',
        'Accept' :'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
        'Accept-Language' : 'fr-fr,en-us;q=0.7,en;q=0.3',
        'Accept-Charset' : 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'
        }
        logging.info('Added post ' + entry['id'])
        req = Request(URL,None,headers)
        response = urlopen(req).read()
        soup = BeautifulSoup(response)
        post_body_str = str(soup.find(id='postingbody'))

        post_id_str = soup.find('p','postinginfo',text=re.compile('post id'))
        post_id = str([int(s) for s in post_id_str.text.split() if s.isdigit()][0])
        f = open(directory+post_id+'.html','w')
        f.write(response)
        f.close()
        time.sleep(15)

def parse_hourly_wage(post):
    '''
    This takes a job post (a post being the souped html file), and
    attempts to find the hourly wage of that job.
    '''
    comp_div = post.find('section','userbody').find('div','bigattr')
    post_string = str(post.find(id='postingbody'))

    if comp_div:
       hr_pay = comp_div.text[len('compensation:')+1:]
    elif '/hr' in post_string:
        pay_index = post_string.index('/hr')
        hr_pay = post_string[pay_index-5:pay_index]
        pay_regex = re.findall(r'[-+]?[0-9]*\.?[0-9]+.',hr_pay)
        if len(pay_regex) > 0:
            hr_pay = pay_regex[0].strip()
    elif 'per hour' in post_string:
        pay_index = post_string.index('per hour')
        hr_pay = post_string[pay_index-5:pay_index]
    elif '$' in post_string:
        pay_index = post_string.index('$')
        hr_pay = post_string[pay_index:pay_index+8]
        hr_pay=''
    else:
        hr_pay = 'n/a'

    if hr_pay is not 'n/a':
        hr_pay = hr_pay.replace(',','')
        pay_regex = re.findall(r'[-+]?[0-9]*\.?[0-9]+.',hr_pay)
        if len(pay_regex) > 0:
            hr_pay = pay_regex[0].strip()
            hr_pay = hr_pay.replace('/','')
            hr_pay = hr_pay.replace('-','')
            hr_pay = hr_pay.replace('+','')
            if hr_pay.isdigit() and float(hr_pay)>25:
                hr_pay = 'n/a'
    return hr_pay

def parse_reply_options(post_soup,post_id):
    '''
    This finds the reply options of that job. This should
    be used sparingly.
    '''
    reply_options_str = []
    if post_soup.find('span','replybelow'):
        reply_options_str.append('reply below')
    elif post_soup.find(id='replylink'):
        URL = 'http://philadelphia.craigslist.org/reply/phi/lab/'+post_id
        html = urlopen(URL).read()
        soup = BeautifulSoup(html)
        reply_options = soup.find('div','reply_options').find('ul').find_all('li')
        for option in reply_options:
            reply_options_str.append(option.text)
    return reply_options_str

def parse_phone_number(body_string):
    '''
    This takes a job post (a post being the souped html file), and
    attempts to find the phone number to contact that job.
    '''
    phone_numbers = re.findall(r'[0-9]{3}[.,-][0-9]{3}[.,-][0-9]{4}',body_string)
    if len(phone_numbers)>0:
        return phone_numbers
    return 'n/a'

def parse_address(post_soup):
    '''
    This takes a job post (a post being the souped html file), and
    attempts to find the address of that job.
    '''
    if post_soup.find('div','mapaddress'):
        return post_soup.find('div','mapaddress').text.rstrip()
    return 'n/a'

def form_text(post):
    '''

    '''
    pay = ''
    address = ''
    phone_number = ''
    if post['pay'] != 'n/a':
        pay_regex = re.findall(r'[-+]?[0-9]*\.?[0-9]+.',post['pay'])
        if len(pay_regex) > 0:
            pay = '$'+post['pay']+'/hr;'
    if post['address'] != 'n/a':
        address = post['address']+';'
    if post['phone_number'] != 'n/a':
        phone_number = post['phone_number'][0]
    text = phone_number+';'+pay+address+post['title']
    return text[:160]

def create_df(directory):
    posts={}
    for filename in glob.glob(directory+'*'):
        f = open(filename,'r')
        soup = BeautifulSoup(f.read())
        post_id = filename[len(directory):filename.index('.html')]
        post ={}
        post['post_id']=post_id
        post['soup']=soup
        body_string = str(soup.find(id='postingbody'))
        post['date_posted']=str(soup.find(id='display-date').text)
        post['title']=soup.find('title').text
        post['pay']=parse_hourly_wage(soup)
        post['address']=parse_address(soup)
        post['body']=body_string
        post['phone_number']=parse_phone_number(body_string)
        post['text'] = form_text(post)
        posts[post_id]=post
    df = pd.DataFrame(posts).T
    return df

def get_valid_texts(df):
    df_new = df[df['phone_number'] != 'n/a']
    for row in df_new.iterrows():
        body_check = row[1]['body']
        if len([True for body in df_new['body'] if difflib.SequenceMatcher(None, body_check, body).ratio() > .25])>1:
            df_new=df_new[df_new.index != row[0]]
    return df_new

def read_rss_and_load(search_type,search_term,directory):
    clist_rss = 'http://philadelphia.craigslist.org/search/'+search_type+'?query='+search_term+'&s=0&format=rss'
    feed = feedparser.parse(clist_rss)
    link_name=feed['entries'][0].id
    file_name=link_name[link_name.rfind('/')+1:]

    if not os.path.exists(directory):
        os.makedirs(directory)
    for entry in feed['entries']:
       load_craigs_page(entry)

def send_mail(to_address,msg):
    from_address = cf['fromaddr']
    # Credentials (if needed)
    username = cf['username']
    password = cf['password']

    # The actual mail send
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username,password)
    server.sendmail(from_address, to_address, msg)
    server.quit()


#Executing of Code
def execute_compemploy():
    read_rss_and_load(search_type,search_term,directory)
    df = create_df(directory)
    df_valid = get_valid_texts(df)
    msg = str(df_valid['text'][len(df_valid)-1])
    practice = ('Sent message: ' + msg + '... with post_id ' +
            df_valid['post_id'][len(df_valid)-1]+' posted on ' +
            df_valid['date_posted'][len(df_valid)-1])
    logging.info(practice)
    send_mail(to_address,practice)

scheduler = BlockingScheduler()
scheduler.add_job(execute_compemploy,'interval',seconds=15)
try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    pass
