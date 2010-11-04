# -*- coding: utf-8 -*-
from google.appengine.ext import db
#from google.appengine.api import users

__name__='dbmodel'


class VPage(db.Expando):
    """ Post of the blog """
    author = db.UserProperty(auto_current_user_add=True)
    title = db.StringProperty()
    name = db.StringProperty()
    content = db.TextProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    language = db.StringProperty()
    comments_enabled = db.BooleanProperty()
    visible = db.BooleanProperty()
    tags = db.StringListProperty()
    
class VPageComment(db.Model):
    """ Blog post comment """
    page_ref = db.ReferenceProperty(reference_class=VPage)
    author = db.UserProperty(auto_current_user_add=True)
    date = db.DateTimeProperty(auto_now_add=True)
    content = db.TextProperty()
    visible = db.BooleanProperty()
    
class VUser(db.Model):
    """ Учетная запись пользователя """
    user = db.UserProperty()
    nickname = db.StringProperty()
    groups = db.StringListProperty()
    
class VUserGroup(db.Model):
    """Описание группы пользователей"""
    name = db.StringProperty()
        
class VTag(db.Model):
    """ Категории страниц """
    name = db.StringProperty()
    title = db.StringProperty()