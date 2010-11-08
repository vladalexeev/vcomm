# -*- coding: utf-8 -*-
import os
#import cgi
#import datetime
#import time
import wsgiref.handlers

#import logging

#from google.appengine.api import users
#from google.appengine.ext import db
from google.appengine.ext import webapp
#from google.appengine.ext.webapp import template

from cms import pages
from cms import admin
from cms import author
from cms import moderator

#import logging

#from customfilters import *

# ===================================================================
# Костыль для Google
# почему-то в библиотеке google.appengine.ext.webapp.template
# переопределялась конфигурация Django, в частности параметр TEMPLATE_DIRS
# из-за чего нельзя было задать последовательность каталогов поиска шаблонов
# 
# Теперь каталоги поиска шаблонов хранятся в переменной BASE_TEMPLATE_DIRS
#
# В случае, если вдруг Google поменяет библиотеку, то данный кусок кода
# надо будет убрать. 
import django.conf
from google.appengine.ext.webapp import template

BASE_TEMPLATE_DIRS = (os.path.abspath('html.override'),os.path.abspath('html.template'),os.path.abspath('html.core'))
def _swap_settings_override(new):
    settings = django.conf.settings
    old = {}
    for key, value in new.iteritems():
        old[key] = getattr(settings, key, None)
        if key == 'TEMPLATE_DIRS' and len(value) > 0:
            value = BASE_TEMPLATE_DIRS + value
        setattr(settings, key, value)
    return old

template._swap_settings = _swap_settings_override
# Конец костыля для Google
# ================================================================


application = webapp.WSGIApplication([
                                      ('/', pages.Page_Index),
                                      (r'/page/(.*)', pages.Page_ShowPage),
                                      ('/pages', pages.Page_PageList),
                                      (r'/tag/(.*)/(.*)/(.*)', pages.Page_PageListByTag),
                                      (r'/tag/(.*)/(.*)', pages.Page_PageListByTag),
                                      (r'/tag/(.*)', pages.Page_PageListByTag),
                                      (r'/pages/author/(.*)', pages.Page_PageListByAuthor),
                                      
                                      ('/admin', admin.AdminPage_AdminHome),
                                      ('/admin/usergroups', admin.AdminPage_UserGroupList),
                                      ('/admin/usergroup/add', admin.AdminAction_UserGroupAdd),
                                      ('/admin/usergroup/delete', admin.AdminAction_UserGroupDelete),
                                      ('/admin/users', admin.AdminPage_UserList),
                                      ('/admin/user/add', admin.AdminAction_UserAdd),
                                      ('/admin/user/delete', admin.AdminAction_UserDelete),
                                      ('/admin/user/profile', admin.AdminPage_UserProfile),
                                      ('/admin/user/save', admin.AdminAction_UserSave),
                                      ('/admin/tags', admin.AdminPage_TagList),
                                      ('/admin/tag/add', admin.AdminAction_TagAdd),
                                      ('/admin/tag/delete', admin.AdminAction_TagDelete),
                                      ('/admin/createsysgroups', admin.AdminAction_CreateSysGroups),
                                      
                                      ('/author/page/edit', author.PageAuthor_EditPage),
                                      ('/author/page/sign', author.ActionAuthor_SignPage),
                                      ('/author/checkpagename', author.AuthorAjax_CheckPageName),
                                      
                                      ('/comment/add', pages.Action_CommentAdd),
                                      
                                      ('/moderator/comment/delete', moderator.ModeratorAction_CommentDelete),
                                      ('/moderator/comment/edit', moderator.ModeratorPage_CommentEdit),
                                      ('/moderator/comment/change', moderator.ModeratorAction_CommentChange),
                                      ('/moderator/user/ban', moderator.ModeratorAction_CommentUserBan),
                                      ('/moderator/user/unban', moderator.ModeratorAction_UserUnban),
                                      ('/moderator/bannedusers', moderator.ModeratorPage_BannedUsers),
                                      ('/moderator/comments', moderator.ModeratorPage_RecentComments)
                                     ], debug=True)

webapp.template.register_template_library('customfilters')
webapp.template.register_template_library('cms.filters')


def main():
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
#    logging.info(str(os.listdir('html')))
    admin.create_sys_groups()
    main()