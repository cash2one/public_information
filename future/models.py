#!/usr/bin/env python
#-*-coding:utf-8-*-
import datetime
import os
import sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String,Text,DateTime,Date,Float,Boolean,ForeignKey
from sqlalchemy import func

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship,backref

from sqlalchemy.ext.declarative import declarative_base


current_directory = os.path.dirname(os.path.abspath(__file__))

#DATABASE_URL = "sqlite:///%s/db.sqlite3" % current_directory
DATABASE_URL = 'mysql://root:Zh-L3z34IokS6fGze@127.0.0.1/test_ras?charset=utf8'
#DATABASE_URL = "mysql://username:password/databasename?charset" % current_directory
engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class TargetUser(Base):
    """
        定义数据库映射
    """
    
    __tablename__ = "target_user"
    
    id = Column(Integer,primary_key=True)
    name = Column(String(32))
    email = Column(String(256),nullable=True) # seperated by "/"
    idcard = Column(String(20),nullable=True)
    qq = Column(String(15),nullable=True)
    phone = Column(String(13),nullable=True)
    audit = Column(Boolean,default=False)
    
    company_id = Column(Integer,ForeignKey("company.id"))
    company = relationship("Company",backref=backref("target_employees",lazy="dynamic"))
    
    def __repr__(self):
        return "<TargetUser %s>" % self.name
        

class Company(Base):

    __tablename__ = "company"
    
    id = Column(Integer,primary_key=True)
    formal_name = Column(String(128))
    nick_name = Column(String(256))
    
    def __repr__(self):
        return "<Company %s>" % self.formal_name
        
class Keyword(Base):
    __tablename__ = "keyword"
    id = Column(Integer,primary_key=True)
    
    company_id = Column(Integer,ForeignKey("company.id"))
    company = relationship("Company",backref=backref("keywords",lazy="dynamic"))
    
    level = Column(Integer,default=0)
    word = Column(String(32))
    word_md5 = Column(String(32),default=func.md5(word))
    
    def __repr__(self):
        return "<Keyword %s>" % self.word
        
class WebPage(Base):

    __tablename__ = "web_page"
    
    id = Column(Integer,primary_key=True)
    url = Column(String(256))
    url_md5 = Column(String(32),default = func.md5(url))
    insert_time = Column(DateTime,default = datetime.datetime.now)
    update_time = Column(DateTime,onupdate=datetime.datetime.now)
    origin_time = Column(Date)
    
    target_user_id = Column(Integer,ForeignKey("target_user.id"))
    target_user = relationship("TargetUser",backref=backref("risky_webpage",lazy="dynamic"))
    
    by_keyword_id = Column(Integer,ForeignKey("keyword.id"))
    by_keyword = relationship("Keyword",backref=backref("related_page",lazy="dynamic"))
    
    score = Column(Float,default=0.0)
    
    plain_text = Column(Text)
    
    def __repr__(self):
        return "<WebPage %s>" % self.score

class SearchResult(Base):
    
    __tablename__ = "search_result"
    
    id = Column(Integer,primary_key=True)
    target_user_id = Column(Integer,ForeignKey("target_user.id"))
    target_user = relationship("TargetUser",backref=backref("search_result_digest",lazy="dynamic"))
    search_condition = Column(String(128))
    item_count = Column(Integer,default=0)
    
    def __repr__(self):
        return "<SearchResult %s>" % self.search_condition            
            

class Console(Base):
    
    __tablename__ = "console"
    
    id = Column(Integer,primary_key=True)
    dataflow = Column(Float,default=0.0)
    user_count = Column(Integer,default=0)
    info_count = Column(Integer,default=0)
    time = Column(DateTime,default=datetime.datetime.now,onupdate=datetime.datetime.now)

    def __repr__(self):
        return "<Console [d]%d [u]%d [i]%s [t]%s>" % (self.dataflow,self.user_count,self.info_count,self.time)   

class PersonStatus(Base):
    __tablename__ = "person_status"
    
    id = Column(Integer,primary_key=True)
    target_user_id = Column(Integer,ForeignKey("target_user.id"))
    target_user = relationship("TargetUser",backref="detail_status") # 这应该是one2one
    score = Column(Float,default=0.0,index=True)
    register_count = Column(Integer,default=0)
    baidu_count = Column(Integer,default=0)
    baidu_score = Column(Float,default=0.0)
    resume_kw_count = Column(Integer,default=0)
    resume_score = Column(Float,default=0.0)
    #resume_text = Column(Text)  #这个resume是不是应该是在resume当中?
    
    def __repr__(self):
        return "<PersonStatus %d>" % self.score    

class RegisterStatus(Base):

    __tablename__="register_status"
    
    id = Column(Integer,primary_key=True)
    target_user_id = Column(Integer,ForeignKey("target_user.id"))
    target_user = relationship("TargetUser",backref=backref("register_status",lazy="dynamic"))
    
    website_name = Column(String(50),default="some website")
    website_logo = Column(String(128),default="/our/own/site/logo.jpg")
    website_url = Column(String(128))
    register_account = Column(String(32))
    
    def __repr__(self):
        return "<RegisterStatus %d>" % self.website_name
        
class Resume(Base):

    __tablename__ = "resume"
    
    id = Column(Integer,primary_key=True)   
    target_user_id = Column(Integer,ForeignKey("target_user.id"))
    target_user = relationship("TargetUser",backref=backref("resume",lazy="dynamic"))
    resume_str = Column(Text)
    getfrom = Column(String(128),default="some url")
        
    def __repr__(self):
        return "<RegisterStatus %d>" % self.target_user.name
                

if __name__ == "__main__":
    """
        直接用python运行这个文件则创建数据库表
        如果更改字段需要删除数据库中对应表格，并重新创建
    """
    Base.metadata.create_all(engine)
