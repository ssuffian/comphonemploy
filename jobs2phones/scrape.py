from bs4 import BeautifulSoup
import time
import feedparser
import re
import os
from urllib2 import urlopen,Request  # for Python 3: from urllib.request import urlopen

def read_rss_and_load(search_type,search_term,directory):
    search_directory = directory + '/' + search_term + '/'
    clist_rss = 'http://philadelphia.craigslist.org/search/'+search_type+'?query='+search_term+'&s=0&format=rss'
    feed = feedparser.parse(clist_rss)
    link_name=feed['entries'][0].id
    file_name=link_name[link_name.rfind('/')+1:]

    if not os.path.exists(search_directory):
        os.makedirs(search_directory)
    for entry in feed['entries']:
       load_craigs_page(entry,search_directory)

def load_craigs_page(entry,search_directory):
    '''
    This method takes an entry from the RSS feed and loads
    sees whether or not that page has been stored. If the page
    has not yet been stored, it stores the page as html file.
    '''
    URL = entry['link']
    link_name = entry['id']
    exist_files = os.listdir(search_directory)

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
        req = Request(URL,None,headers)
        response = urlopen(req).read()
        soup = BeautifulSoup(response)
        post_body_str = str(soup.find(id='postingbody'))

        post_id_str = soup.find('p','postinginfo',text=re.compile('post id'))
        post_id = str([int(s) for s in post_id_str.text.split() if s.isdigit()][0])
        f = open(search_directory+post_id+'.html','w')
        f.write(response)
        f.close()
        time.sleep(15)
