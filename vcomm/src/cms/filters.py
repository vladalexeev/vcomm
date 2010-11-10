# -*- coding: utf-8 -*-
from google.appengine.ext.webapp import template
from google.appengine.api import memcache

from db.dbmodel import VTag
from db.dbmodel import VUser
import misc

logger = misc.LoggerWrapper()

mm_cache = memcache.Client()

def tag_title(name):
    """Фильтр, преобразующий имя тега в его отображаемое значение"""
    memcache_name = 'vtag_'+name
    memcache_value = mm_cache.get(memcache_name)
    
    if memcache_value is not None:
        return memcache_value
    else:
        memcache_value = name
        tag = VTag.all().filter('name =', name).get()
        if tag:
            memcache_value = tag.title
        mm_cache.add(memcache_name,memcache_value,3600)
        return memcache_value
    
def vuser_id(user_prop):
    """Фильтр, получающий id пользователя по его UserProperty"""
    memcache_name = 'vuser_id_'+str(user_prop.email)

    memcache_value = mm_cache.get(memcache_name)
    
    if memcache_value is not None:
        return memcache_value
    else:
        vuser = VUser.all().filter('user =', user_prop).get()
        if vuser:
            logger.info('vuser id ='+str(vuser.key().id()))
            memcache_value = str(vuser.key().id())
            mm_cache.add(memcache_name, memcache_value,3600)
            return memcache_value
        else:
            return None

def vuser_nickname(user_prop):
    """Фильтр, получающий nickname пользователя по его UserProperty"""
    memcache_name = 'vuser_nickname_'+str(user_prop.email)
    memcache_value = mm_cache.get(memcache_name)
    
    if memcache_value is not None:
        return memcache_value
    else:
        vuser = VUser.all().filter('user =', user_prop).get()
        memcache_value = user_prop.nickname()
        if vuser and vuser.nickname:
            memcache_value = vuser.nickname
            
        mm_cache.add(memcache_name, memcache_value,3600)
        return memcache_value
    
page_cut_start = '<pagecut>'
page_cut_end = '</pagecut>'

def page_text_cut(page):
    text = page.content
    n = text.find(page_cut_start)
    n2 = text.find(page_cut_end)
    
    if n>=0:
        if n2<n:
            return text[:n-1]+'<a href="/page/'+page.name+'">...</a>'
        else:
            atext = text[n+len(page_cut_start):n2]
            if not atext:
                atext='...'
            return text[:n-1]+'<a href="/page/'+page.name+'">'+atext+'</a>'
    else:
        return text
    
def page_text_full(page):
    text = page.content
    n = text.find(page_cut_start)
    n2 = text.find(page_cut_end)
    
    if n>=0:
        if n2<n:
            return text[:n-1]+text[n+len(page_cut_start):]
        else:
            return text[:n-1]+text[n2+len(page_cut_end):]
    else:
        return text;

register = template.create_template_register()
register.filter(tag_title)
register.filter(vuser_id)
register.filter(vuser_nickname)

register.filter(page_text_cut)
register.filter(page_text_full)