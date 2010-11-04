# -*- coding: utf-8 -*-
#import os
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

#from customfilters import *


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
                                      
                                      ('/author/page/edit', author.PageAuthor_EditPage),
                                      ('/author/page/sign', author.ActionAuthor_SignPage),
                                      
                                      ('/comment/add', pages.Action_CommentAdd),
                                      
                                      ('/moderator/comment/delete', moderator.ModeratorAction_CommentDelete),
                                      ('/moderator/comment/edit', moderator.ModeratorPage_CommentEdit),
                                      ('/moderator/comment/change', moderator.ModeratorAction_CommentChange)
                                     ], debug=True)

webapp.template.register_template_library('customfilters')
webapp.template.register_template_library('cms.filters')


def main():
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()