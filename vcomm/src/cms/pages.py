# -*- coding: utf-8 -*-


import misc

from base import LoggedInRequestHandler
from base import BasicRequestHandler
from base import BasicRequestHandlerException
from db.dbmodel import VPage
from db.dbmodel import VPageComment

logger = misc.LoggerWrapper()

page_size = 5

class Page_Index(BasicRequestHandler):
    """Обработчик индексной страницы"""
    def get(self):
        start_index=0
        
        template_values = getPages(start_index, page_size, self.user_info)
                
        self.write_template('html/index.html', template_values)
        
class Page_PageList(BasicRequestHandler):
    """Обработчик страницы анонсов в обратном хронологическом порядке"""
    def get(self):
        start_index = 0
        if (self.request.get("start")):
            start_index=int(self.request.get("start"))
            
        template_values = getPages(start_index, page_size, self.user_info)
        self.write_template('html/page-list.html', template_values)
        
class Page_PageListByTag(BasicRequestHandler):
    """Обработчик страницы анонсов страниц по конкретному тегу
      в обратном хронологическом порядке
    """
    def get(self, *args):
        logger.info("args "+str(args))
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
        template_values['tag_name'] = tag_names        
        self.write_template('html/page-list-tag.html', template_values)
        
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

class Page_ShowPage(BasicRequestHandler): 
    def get(self,*ar):
        page_name = ar[0]
        
        page = VPage.all().filter('name',page_name).get()
        if page:
            comments = VPageComment.all().filter('page_ref', page)
            template_values = {
                               'page': page,
                               'comments': comments
                               }
            self.write_template('/html/page-show.html', template_values)
        else:
            raise BasicRequestHandlerException(404,'Page not found name='''+page_name+"'")
        
class Action_CommentAdd(LoggedInRequestHandler):
    def post(self):
        page_key = self.request.get('key')
        page = VPage.get(page_key)
        
        comment = VPageComment()
        comment.content = self.request.get('content')
        comment.visible = True
        comment.page_ref = page
        comment.put()
        
        self.redirect('/page/'+page.name)