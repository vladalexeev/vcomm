# -*- coding: utf-8 -*-


import misc

from base import LoggedInRequestHandler
from base import BasicRequestHandler
from base import BasicRequestHandlerException
from db.dbmodel import VPage
from db.dbmodel import VPageComment
from db.dbmodel import VUser
from db.dbmodel import VTag

from google.appengine.ext import db

logger = misc.LoggerWrapper()

page_size = 5

class Page_BasicRequestHandler(BasicRequestHandler):
    def write_template(self, template_name, template_values):
        tags = VTag.all().order('title')
        template_values['tags'] = tags
        super(Page_BasicRequestHandler, self).write_template(template_name,template_values)

class Page_Index(Page_BasicRequestHandler):
    """Обработчик индексной страницы"""
    def get(self):
        start_index=0
        
        template_values = getPages(start_index, page_size, self.user_info)
                
        self.write_template('html.template/index.html', template_values)
        
class Page_PageList(Page_BasicRequestHandler):
    """Обработчик страницы анонсов в обратном хронологическом порядке"""
    def get(self):
        start_index = 0
        if (self.request.get("start")):
            start_index=int(self.request.get("start"))
            
        template_values = getPages(start_index, page_size, self.user_info)
        self.write_template('html.template/page-list.html', template_values)
        
class Page_PageListByTag(Page_BasicRequestHandler):
    """Обработчик страницы анонсов страниц по конкретному тегу
      в обратном хронологическом порядке
    """
    def get(self, *args):
        start_index = 0
        if (self.request.get("start")):
            start_index=int(self.request.get("start"))
            
        tag_names = args
        url_template = '/tag'
        for tag_name in tag_names:
            url_template += '/'+tag_name
        url_template += '?start='
        
        template_values = getPages(start_index, page_size, self.user_info, url_template,
                                   (lambda query: tagFilterList(query,tag_names)))
        template_values['tag_names'] = tag_names        
        self.write_template('html.template/page-list-tag.html', template_values)
        
class Page_PageListByAuthor(Page_BasicRequestHandler):
    def get(self, *args):
        logger.info("Auhtor args "+str(args))
        start_index = 0
        if (self.request.get("start")):
            start_index=int(self.request.get("start"))
            
        author_id = args[0]
        url_template = '/pages/author/'+author_id
        
        logger.info('author_id='+str(author_id))
        
        vuser_key = db.Key.from_path('VUser',int(author_id))
        vuser = VUser.get(vuser_key)
        
        if vuser:        
            template_values = getPages(start_index, page_size, self.user_info, url_template,
                                       (lambda query: query.filter('author =',vuser.user)))
            template_values['author'] = vuser       
            self.write_template('html.template/page-list-author.html', template_values)
        else:
            raise BasicRequestHandlerException(404,'User not found id='+author_id)        
        
def tagFilterList(query, tag_names):
    """Создание фильтра для запроса для выборки страниц по нескольким тегам"""
    for tag in tag_names:
        logger.info("add filter tag "+tag)
        query = query.filter('tags =', tag)
        
    return query

def getPages(start_index, page_size, user_info, 
             url_template = '/pages?start=', filter_lambda = None):
    """Получение постов для страничного отображения.
    
    Args:
        start_index - начальный индекс страницы
        page_size - количество анонсов на странице
        user_info - информация о текущем пользователе
        url_template - шаблон URL для перехода на следующую и предыдущую страницу
        filter_lambda - лямбда-функция для дополнительной фильтрации запроса.
           на вход функции поступает запрос к БД, на выходе - фильтрованый запрос
        
    Returns:
       словарь с тремя параметрами: pages,prev_page_url,next_page_url
    """
    pages_query=VPage.all()
        
    if not user_info.admin:
        pages_query = pages_query.filter('visible =',True)
        
    if filter_lambda:
        pages_query = filter_lambda(pages_query)

    pages_query = pages_query.order('-date')
            
    pages = pages_query.fetch(page_size+1,start_index)

    if start_index == 0:
        prev_page_url = None
    elif start_index-page_size <= 0:
        prev_page_url = url_template+'0'
    else:
        prev_page_url = url_template+str(start_index-page_size)

    if len(pages) > page_size:
        next_page_url = url_template+str(start_index+page_size)
    else:
        next_page_url = None
            
    if len(pages) > page_size:
        visible_pages = pages[:-1]
    else:
        visible_pages = pages

    template_values = {
                        'pages': visible_pages,
                        'pages_prev_page_url': prev_page_url,
                        'pages_next_page_url': next_page_url
                      }
    
    return template_values       

class Page_ShowPage(Page_BasicRequestHandler): 
    def get(self,*ar):
        page_name = ar[0]
        
        page = VPage.all().filter('name',page_name).get()
        if page:
            comments = VPageComment.all().filter('page_ref', page)
            template_values = {
                               'page': page,
                               'comments': comments
                               }
            self.write_template('html.template/page-show.html', template_values)
        else:
            raise BasicRequestHandlerException(404,'Page not found name='''+page_name+"'")
        
class Action_CommentAdd(LoggedInRequestHandler):
    def post(self):
        if self.user_info.banned:
            raise BasicRequestHandlerException(403,'User banned')
        
        page_key = self.request.get('key')
        page = VPage.get(page_key)
        
        comment = VPageComment()
        comment.content = self.request.get('content')
        comment.visible = True
        comment.page_ref = page
        comment.put()
        
        self.redirect('/page/'+page.name)