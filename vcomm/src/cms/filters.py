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

register = template.create_template_register()
register.filter(tag_title)
register.filter(vuser_id)
register.filter(vuser_nickname)