# -*- coding: utf-8 -*-

from google.appengine.ext import db

from base import AuthorRequestHandler
from base import BasicRequestHandlerException

from db.dbmodel import VPage
from db.dbmodel import VTag
import logging
import re

class PageAuthor_EditPage(AuthorRequestHandler):
    def get(self):
        super(PageAuthor_EditPage,self).get()
        pageKey = self.request.get('key')
        page= None
        if pageKey:
            page = VPage.get(pageKey)
            if page.author <> self.user_info.user and not self.user_info.admin:
                raise BasicRequestHandlerException(403,'Cannot edit page. Not author or admin')
            
        tags = VTag.all()
            
        template_values = {
                           'page': page,
                           'tags': tags
                           }
        self.write_template('html.core/author-page-add.html', template_values)

class ActionAuthor_SignPage(AuthorRequestHandler):
    def post(self):
        super(ActionAuthor_SignPage,self).post()
        page_key = self.request.get('key')
        page_name = self.request.get('page_name')
        if not check_page_name(page_key, page_name):
            raise BasicRequestHandlerException(500,'Invalid page name "'+page_name+'"')
        
        if page_key:
            page = VPage.get(page_key)
            if page.author <> self.user_info.user and not self.user_info.admin:
                raise BasicRequestHandlerException(403,'Cannot edit page. Not author or admin')
        else:
            page = VPage()
            page.tags = []
            
        page.title = self.request.get('page_title')
        page.name = page_name
        if self.request.get('page_visible'):
            page.visible = True
        else:
            page.visible = False
        page.content = self.request.get('page_content')
        
        all_tags = VTag.all()
        page_tags = []
        for tag in all_tags:
            if self.request.get('tag_'+tag.name):
                page_tags += [tag.name]
                
        page.tags = page_tags
        
        page.put()
            
        self.redirect('/author/page/edit?key='+str(page.key()))
        
class AuthorAjax_CheckPageName(AuthorRequestHandler):
    """Проверка аяксом уникальности имени страницы"""
    def get(self):
        page_key = self.request.get('key')
        page_name = self.request.get('name')
        
        if check_page_name(page_key, page_name):
            self.response.out.write('setPageNameCorrect(true)')
        else:
            self.response.out.write('setPageNameCorrect(false)')
        
def check_page_name(page_key, page_name):
    """Функция проверяет существует ли еще хотя бы одна страница
    с заданным именем за исключением страницы с ключом page_key"""
    r = r'[^a-zA-z0-9-.]'
    if re.match(r, page_name):
        logging.info('page name is incorrent "'+page_name+'"')
        return False
    
    query = VPage.all().filter('name =', page_name)
    if page_key:
        query = query.filter('__key__ !=',db.Key(page_key))
        
    if query.get():
        return False
    else:
        return True