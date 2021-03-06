# -*- coding: utf-8 -*-

from google.appengine.api.users import User

import misc
import const

from base import AdminRequestHandler

from db.dbmodel import VUserGroup
from db.dbmodel import VUser
from db.dbmodel import VTag

from google.appengine.ext import db

logger = misc.LoggerWrapper()

def create_user_group_if_not_exist(group_name):
    """Создание группы пользователей, если она еще не существует"""
    user_group = VUserGroup.all().filter('name =', group_name).get()
    if not user_group:
        user_group = VUserGroup()
        user_group.name = group_name
        user_group.put()
        
def create_sys_groups():
    """Создание системных групп пользователей"""
    for group_name in const.sys_groups:
        create_user_group_if_not_exist(group_name)

class AdminPage_AdminHome(AdminRequestHandler):
    """Домашняя страница администрирования"""
    def get(self):
        super(AdminPage_AdminHome,self).get()
        template_values = {
                           'version':const.version
                           }
        self.write_template('html.core/admin-home.html', template_values)

class AdminPage_UserGroupList(AdminRequestHandler):
    """Обработчик страницы групп пользователей"""
    def get(self):
        super(AdminPage_UserGroupList,self).get()
        userGroups = VUserGroup.all()
        template_values={
                         'userGroups': userGroups,
                         'sys_groups': const.sys_groups
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
        if not g.name in const.sys_groups:
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
        if self.request.get('key'):
            user = VUser.get(self.request.get('key'))
        else:
            key = db.Key.from_path('VUser',int(self.request.get('id')))
            user = VUser.get(key)
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
    """Страница для отображения тегов"""
    def get(self):
        super(AdminPage_TagList,self).get()
        tags = VTag.all()
        template_values = {
                           'tags':tags
                           }
        self.write_template('html.core/admin-tags.html', template_values)
        
class AdminAction_TagAdd(AdminRequestHandler):
    """Действие добавления тега"""
    def post(self):
        super(AdminAction_TagAdd,self).post()
        tag = VTag()
        tag.name = self.request.get("tag_name")
        tag.title = self.request.get("tag_title")
        tag.put()
        self.redirect('/admin/tags')
        
class AdminAction_TagDelete(AdminRequestHandler):
    """Действие удаления тега"""
    def get(self):
        super(AdminAction_TagDelete,self).get()
        tag_key = self.request.get('key')
        tag = VTag.get(tag_key)
        VTag.delete(tag)
        self.redirect('/admin/tags')
        
class AdminAction_CreateSysGroups(AdminRequestHandler):
    """Действие по созданию системных групп"""
    def get(self):
        super(AdminAction_CreateSysGroups,self).get()
        create_sys_groups()
        self.redirect('/admin/usergroups')