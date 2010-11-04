# -*- coding: utf-8 -*-

from google.appengine.api.users import User

import misc

from base import AdminRequestHandler

from db.dbmodel import VUserGroup
from db.dbmodel import VUser
from db.dbmodel import VTag

logger = misc.LoggerWrapper()

class AdminPage_AdminHome(AdminRequestHandler):
    """Домашняя страница администрирования"""
    def get(self):
        super(AdminPage_AdminHome,self).get()
        self.write_template('html.core/admin-home.html', {})

class AdminPage_UserGroupList(AdminRequestHandler):
    """Обработчик страницы групп пользователей"""
    def get(self):
        super(AdminPage_UserGroupList,self).get()
        userGroups = VUserGroup.all()
        template_values={
                         'userGroups': userGroups
                         }
        self.write_template('html.core/admin-user-groups.html', template_values)
        
class AdminAction_UserGroupAdd(AdminRequestHandler):
    """Добавление описания группы пользователей"""
    def post(self):
        super(AdminAction_UserGroupAdd,self).get()
        g = VUserGroup()
        g.name = self.request.get('group_name')
        g.put()
        
        self.redirect("/admin/usergroups")
        
class AdminAction_UserGroupDelete(AdminRequestHandler):
    """Удаление описания группы пользователей"""
    def get(self):
        super(AdminAction_UserGroupDelete,self).get()
        g = VUserGroup.get(self.request.get('key'))
        VUserGroup.delete(g)
        self.redirect('/admin/usergroups')
        
class AdminPage_UserList(AdminRequestHandler):
    """Список пользователей"""
    def get(self):
        super(AdminPage_UserList,self).get()
        users = VUser.all()
        
        template_values = {
                           'users': users
                           }
        self.write_template('html.core/admin-users.html', template_values)
        
class AdminAction_UserAdd(AdminRequestHandler):
    """Добавление пользователя"""
    def post(self):
        super(AdminAction_UserAdd,self).get()
        u = User(email=self.request.get('user_email'))
        existUser=VUser.all().filter('user=', u).get()
        
        if not existUser:        
            newUser = VUser()
            newUser.user = User(email=self.request.get('user_email'))
            newUser.put()
            
        self.redirect('/admin/users')
        
class AdminAction_UserDelete(AdminRequestHandler):
    """Удаление пользователя"""
    def get(self):
        super(AdminAction_UserDelete,self).get()
        u = VUser.get(self.request.get('key'))
        VUser.delete(u)
        self.redirect('/admin/users')
        
class AdminPage_UserProfile(AdminRequestHandler):
    """Страница профиля пользователя"""
    def get(self):
        super(AdminPage_UserProfile,self).get()
        user = VUser.get(self.request.get('key'))
        groups = VUserGroup.all()
        template_values = {
                           'user': user,
                           'groups': groups,
                           'userGroups': user.groups
                           }
        self.write_template('html.core/admin-user-profile.html', template_values)
        
class AdminAction_UserSave(AdminRequestHandler):
    """Сохранение профиля пользователя"""
    def post(self):
        super(AdminAction_UserSave,self).get()
        user = VUser.get(self.request.get('key'))
        groups = VUserGroup.all()
        
        userGroups = []
        for group in groups:
            if self.request.get('group_'+group.name) <> '':
                userGroups += [group.name]
                
        user.groups = userGroups
        user.nickname = self.request.get('nickname')
        user.put()
        
        self.redirect('/admin/user/profile?key='+str(user.key()))
        
class AdminPage_TagList(AdminRequestHandler):
    def get(self):
        super(AdminPage_TagList,self).get()
        tags = VTag.all()
        template_values = {
                           'tags':tags
                           }
        self.write_template('html.core/admin-tags.html', template_values)
        
class AdminAction_TagAdd(AdminRequestHandler):
    def post(self):
        super(AdminAction_TagAdd,self).post()
        tag = VTag()
        tag.name = self.request.get("tag_name")
        tag.title = self.request.get("tag_title")
        tag.put()
        self.redirect('/admin/tags')
        
class AdminAction_TagDelete(AdminRequestHandler):
    def get(self):
        super(AdminAction_TagDelete,self).get()
        tag_key = self.request.get('key')
        tag = VTag.get(tag_key)
        VTag.delete(tag)
        self.redirect('/admin/tags')