from sqlalchemy import create_engine
from sqlalchemy import MetaData, Column, Table
from sqlalchemy import Integer, String, DateTime, Boolean
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
import datetime
import yaml
with open('../config.yaml') as f:
    cf = yaml.safe_load(f)
Base = declarative_base()

class Post(Base):
    __tablename__ = 'posts'
    id = Column('id', String, primary_key=True)
    address = Column('address', String(200))
    body = Column('body', String(10000))
    date_posted = Column('date_posted', DateTime)
    pay = Column('pay',String(200))
    phone_number = Column('phone_number',String(100))
    new = Column('new',Boolean)
    text = Column('text',String(140))
    search_criteria = Column('search_criteria',String(140))

class User(Base):
    __tablename__ = 'users'
    password = Column('password', String)
    email_address = Column('email_address', String)
    phone_number = Column('phone_number', String, primary_key=True)
    search_criteria = Column('search_criteria', String, nullable=False)
    posts_sent_count = Column('posts_sent_count',Integer)


class UserInserter(object):
    def insert(self,session,email_address,phone_number,password,search_criteria):
        if len(session.query(User).filter(User.phone_number==phone_number).all())==0:
            new_user = User(email_address=email_address, phone_number=phone_number,password=password,
                        search_criteria=search_criteria,posts_sent_count=0)
            session.merge(new_user)

class UserReader(object):
    def read(self,session, search_criteria):
        users = []
        for i,user in enumerate(session.query(User).filter(User.search_criteria==search_criteria)):
            users.append(user.phone_number)
        return users

class PostInserter(object):
    def insert(self,session,row):
        if len(session.query(Post).filter(Post.id==row['post_id']).all())==0:
            new_post = Post(id=row['post_id'], address=row['address'], body=row['body'],
                     date_posted=datetime.datetime.strptime(row['date_posted'], "%Y-%m-%d %I:%M%p") ,
                     pay=row['pay'],phone_number=row['phone_number'], new=row['new'], text=row['text'],
                     search_criteria=row['search_term'])
            session.add(new_post)

class PostReader(object):
    def read(self,session):
        posts = []
        for i,post in enumerate(session.query(Post).filter(Post.new==True)):
            posts.append([post.text,post.search_criteria])
        return posts

class PostMarker(object):
    def mark(self,session,post):
        updated_post = session.query(Post).filter(Post.text==post)[0]
        updated_post.new = False
        session.merge(updated_post)

class PostsCountIncrementer(object):
    def increment(self,session,phone_number):
        user = session.query(User).filter(User.phone_number==phone_number)[0]
        user.posts_sent_count = user.posts_sent_count + 1
        session.merge(user)

@contextmanager
def session_scope(Session):
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def mark_post(Session,post):
    with session_scope(Session) as session:
        return PostMarker().mark(session,post)

def load_data(Session,df_valid):
    with session_scope(Session) as session:
        for i,row in df_valid.iterrows():
            PostInserter().insert(session,row)

def read_new_data(Session):
    with session_scope(Session) as session:
        return PostReader().read(session)

def read_interested_users(Session,search_criteria):
    with session_scope(Session) as session:
        return UserReader().read(session,search_criteria)

def insert_user(Session,email_address,phone_number,password,search_criteria):
    with session_scope(Session) as session:
        UserInserter().insert(session,email_address,phone_number,password,search_criteria)

def increment_posts_sent_count(Session,phone_number):
    with session_scope(Session) as session:
        return PostsCountIncrementer().increment(session,phone_number)

def bind_to_database(username,password,db_name):
    engine = create_engine('postgresql://'+username+':'+
            password+'@localhost/'+db_name)
    Session = sessionmaker(bind=engine)
    return Session
