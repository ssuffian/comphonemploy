import load
import send
import imaplib
import email
import yaml
import re
from bs4 import BeautifulSoup


with open('../config.yaml') as f:
    cf = yaml.safe_load(f)

def parse_text_message_from_email(msg):
    '''
    Gets the actual text sent to the 
    email address by parsing it out of the email body
    '''
    text = {}
    text['sender'] = msg['from']
    if msg.is_multipart():
        for i,part in enumerate(msg.walk()):
            if part.get_content_type() =='text/plain':
                msg_body = part.get_payload(decode=True)
    else:
        msg_body = msg.get_payload(decode=True)
    msg_body.replace('\r','').replace('\n','')
   
    text['message']=msg_body
    return text


def parse_choices(choices_made):
    '''
    Takes a numbered list of choices and maps them 
    to the relevant search criteria.
    '''
    search_criteria='';
    for choice in choices_made:
        if choice == '1':
            search_criteria='dishwasher&20philadelphia ' + search_criteria
        if choice == '2':
            search_criteria='warehouse&20philadelphia ' + search_criteria
        if choice == '3':
            search_criteria='cook&20philadelphia ' + search_criteria
    return search_criteria

def read_mailbox_and_edit_users(M):
    """
    Processes mail in order to add,edit, and remove users
    """
    Session = load.bind_to_database(cf['postgres_username'],cf['postgres_password'],
        cf['postgres_db'])
    rv, data_num = M.search(None, "ALL")
    if rv != 'OK':
        print "No messages found!"
        return
                    
    messages=[]
    print str(len(data_num[0].split())) + " new messages found"
    for num in data_num[0].split():
        rv, data = M.fetch(num, '(RFC822)')
        if rv != 'OK':
            print "ERROR getting message", num
            return
        email_data = email.message_from_string(data[0][1])
        text = parse_text_message_from_email(email_data)
        choices_made = re.findall(r'\d+',text['message'])
        if 'stop' in text['message'].lower():
            if load.check_user(Session,text['sender']):
                load.delete_user(Session,text['sender'])
            send.send_text(cf['fromaddr'],cf['username'],cf['password'],text['sender'],
                cf['stop_message'])
            M.store(num , '+FLAGS', '\\Deleted') #This archives the message.
        elif 'start' in text['message'].lower() or 'list' in text['message'].lower():
            send.send_text(cf['fromaddr'],cf['username'],cf['password'],text['sender'],
                cf['start_message'])
            M.store(num , '+FLAGS', '\\Deleted') #This archives the message.
        elif len(choices_made) > 0:
            search_criteria = parse_choices(choices_made)
            if len(search_criteria) > 0:
                if load.check_user(Session,text['sender']):
                    load.edit_user(Session,text['sender'],search_criteria)
                else:
                    load.insert_user(Session,'',text['sender'],'',search_criteria)
                send.send_text(cf['fromaddr'],cf['username'],cf['password'],text['sender'],
                              str(choices_made) + '. ' + cf['chosen_message'])
                M.store(num , '+FLAGS', '\\Deleted') #This archives the message.

