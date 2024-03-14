from store.database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship

class USER(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index = True)
    firstname = Column(String, nullable= False)
    lastname = Column(String, nullable= False)
    email = Column(String, nullable= False, unique=True)
    password = Column(String, nullable= False, index= True) 
    
    urls = relationship("URL", back_populates = "owner")


class URL(Base):
    __tablename__ = 'urls'
    
    id = Column(Integer, primary_key=True, index = True)
    title = Column(String, nullable=True, default="My Title")
    destination = Column(String, nullable=True)
    key = Column(String, nullable= False, unique=True)
    clicks = Column(Integer, default=0)
    date_created = Column(Date, nullable= False)
    owner_id = Column(Integer, ForeignKey("users.id"), default=0)
    owner = relationship("USER", back_populates = "urls")