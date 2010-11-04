# -*- coding: utf-8 -*-
from google.appengine.ext.webapp import template
from google.appengine.api import memcache

from db.dbmodel import VTag
import misc

logger = misc.LoggerWrapper()

mm_cache = memcache.Client()

def tag_title(name):
    """Фильтр, преобразующий имя тега в его отображаемое значение"""
    memcache_name = 'tag_'+name
    memcache_value = mm_cache.get(memcache_name)
    
    if memcache_value is not None:
        return memcache_value
    else:
        memcache_value = name
        tag = VTag.all().filter('name =', name).get()
        if tag:
            memcache_value = tag.title
        mm_cache.add(memcache_name,memcache_value)
        return memcache_value


register = template.create_template_register()
register.filter(tag_title)