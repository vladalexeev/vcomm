# -*- coding: utf-8 -*-

import os

from google.appengine.api import users
#from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from misc import LoggerWrapper

from db.dbmodel import VUser
import const

logger=LoggerWrapper()

class UserInfo:
    """ Информация о пользователе для страницы """
    user=None
    user_name=''
    
    superadmin = False
    admin = False
    banned = False
    author = False
    moderator = False
    
    login_url=None
    login_url_text=None
    
    groups=[]
    
    url_my_cubic_figures = None
    url_create_cubic_figure = None
    url_add_post = None
    
    def __init__(self,request_uri):
        self.user=users.get_current_user()
        if users.get_current_user():
            self.user_name=users.get_current_user().nickname()
            self.superadmin = users.is_current_user_admin()
            
            self.login_url=users.create_logout_url('/')
            self.login_url_text='Logout'
            
            vuser = VUser.all().filter('user', self.user).get()
            if vuser:
                self.groups = vuser.groups
                
            self.banned = const.sys_group_banned in self.groups
            self.admin = const.sys_group_admin in self.groups
            self.moderator = const.sys_group_moderator in self.groups
            self.author = const.sys_group_author in self.groups
            
            if self.banned:
                self.admin = False
                self.author = False
                self.moderator = False
                self.groups = [const.sys_group_banned]
                
            if self.admin:
                self.author = True
                self.moderator = True
                
            if self.superadmin:
                self.banned = False
                self.admin = True
                self.author = True
                self.moderator = True
                self.groups.append('superadmin')
            
        else:
            self.login_url=users.create_login_url(request_uri)
            self.login_url_text='Login into Google account'
            
class BasicRequestHandlerException(Exception):
    def __init__(self,code,message):
        self.code = code
        self.message = message            
            
class BasicRequestHandler(webapp.RequestHandler):
    def initialize(self, request, response):
        webapp.RequestHandler.initialize(self, request, response)
        self.user_info=UserInfo(self.request.uri)
        
    def write_template(self,template_name,template_values):
        """Вывод шаблона в выходной поток"""
        template_values['user_info']=self.user_info
        path = os.path.join(os.path.dirname(__file__), "../"+template_name)
        self.response.out.write(template.render(path, template_values))
        
    def handle_exception(self, exception, debug_mode):
        if isinstance(exception, BasicRequestHandlerException):
            logger.error("Request handler exception code="+str(exception.code)+" - "+str(exception.message))
            self.error(exception.code)
        else:
            logger.error("Exception "+str(exception))
            super(BasicRequestHandler,self).handle_exception(exception,debug_mode)
            
class LoggedInRequestHandler(BasicRequestHandler):
    def get(self):
        if not self.user_info.user:
            raise BasicRequestHandlerException(403,'Not logged in')
        
    def post(self):
        if not self.user_info.user:
            raise BasicRequestHandlerException(403, 'Not logged in')
        
class AdminRequestHandler(LoggedInRequestHandler):
    """Обработчик запроса, проверяющий права администратора автоматически"""
    def get(self):
        super(AdminRequestHandler,self).get()
        if not self.user_info.admin:
            raise BasicRequestHandlerException(403, 'Not admin')
        
   
    def post(self):
        super(AdminRequestHandler,self).post()
        if not self.user_info.admin:
            raise BasicRequestHandlerException(403, 'Not admin')
        
class AuthorRequestHandler(LoggedInRequestHandler):
    """Обработчик запроса, проверяющий право писать статьи автоматически"""
    def get(self):
        super(AuthorRequestHandler,self).get()
        if not self.user_info.author:
            raise BasicRequestHandlerException(403, 'Not author')
        
   
    def post(self):
        super(AuthorRequestHandler,self).post()
        if not self.user_info.author:
            raise BasicRequestHandlerException(403, 'Not author')
        
class ModeratorRequestHandler(LoggedInRequestHandler):
    """Обработчик запроса, проверяющий право модерирования"""
    def get(self):
        super(ModeratorRequestHandler,self).get()
        if not self.user_info.moderator:
            raise BasicRequestHandlerException(403, 'Not moderator')
        
   
    def post(self):
        super(ModeratorRequestHandler,self).post()
        if not self.user_info.moderator:
            raise BasicRequestHandlerException(403, 'Not moderator')
