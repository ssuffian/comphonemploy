import smtplib
import load

def send_text(from_addrs,username,password,to_addrs,msg):

    # The actual mail send
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username,password)
    server.sendmail(from_addrs, to_addrs, msg)
    server.quit()

def send_from_database(Session):
    posts = load.read_new_data(Session)
    for post in posts:
        phone_numbers = load.read_interested_users(Session,post[1])
        for phone_number in phone_numbers:
            send_text(cf['fromaddr'],cf['username'],cf['password'],phone_number,post[0])
            load.mark_post(Session,post[0])
            load.increment_posts_sent_count(Session,phone_number)
