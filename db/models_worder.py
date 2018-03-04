#!/usr/bin/env python
#encoding=utf-8
from sqlalchemy import create_engine, Column, Boolean, DateTime, Text, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool

from etc.conf import *

engine = create_engine(sql_connection_worder, convert_unicode=True, poolclass=NullPool)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def worder_init_db():
    Base.metadata.create_all(bind=engine)


class Worder(Base):
    __tablename__ = "worder"
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    deleted = Column(Boolean, default=False)
    id = Column(VARCHAR(36), primary_key=True)
    user_id = Column(VARCHAR(100))
    title = Column(VARCHAR(200))
    describe = Column(Text)
    about_id = Column(VARCHAR(200))
    app_service_id = Column(VARCHAR(36))
    status = Column(Boolean, default=False)
    treat_user_id = Column(VARCHAR(100))
    user_name = Column(VARCHAR(100))
    auth_name = Column(VARCHAR(100))
    auth_id = Column(VARCHAR(100))
    auth_phone = Column(VARCHAR(20))


class APPService(Base):
    __tablename__ = "app_service"
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    deleted = Column(Boolean, default=False)
    id = Column(VARCHAR(36), primary_key=True)
    name = Column(VARCHAR(20))
    type_id = Column(VARCHAR(36))


def register_models(tables):
    """Register Models and create metadata.
    tablese = (Costlog,)
    """
    models = tables
    for model in models:
        model.metadata.create_all(engine)

