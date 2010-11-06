# -*- coding: utf-8 -*-

from base import ModeratorRequestHandler
from db.dbmodel import VPageComment
from db.dbmodel import VUser

import const

class ModeratorAction_CommentDelete(ModeratorRequestHandler):
    def get(self):
        super(ModeratorAction_CommentDelete,self).get()
        comment_key = self.request.get('key')
        comment = VPageComment.get(comment_key)
        VPageComment.delete(comment)
        if self.request.get('return'):
            self.redirect(self.request.get('return'))

class ModeratorPage_CommentEdit(ModeratorRequestHandler):
    def get(self):
        super(ModeratorPage_CommentEdit,self).get()
        comment_key = self.request.get('key')
        return_target = self.request.get('return')
        comment = VPageComment.get(comment_key)
        template_values = {
                           'comment': comment,
                           'return_target': return_target
                           }
        self.write_template('html.core/moderator-comment-edit.html', template_values)
        
class ModeratorAction_CommentChange(ModeratorRequestHandler):
    def post(self):
        super(ModeratorAction_CommentChange,self).post()
        comment_key = self.request.get('key')
        return_target = self.request.get('return')
        comment = VPageComment.get(comment_key)
        comment.content = self.request.get('content')
        comment.put()
        if return_target:
            self.redirect(return_target)
            
class ModeratorAction_CommentUserBan(ModeratorRequestHandler):
    def get(self):
        super(ModeratorAction_CommentUserBan,self).get()
        comment_key = self.request.get('key')
        comment = VPageComment.get(comment_key)
        
        vuser = VUser.all().filter('user =', comment.author).get()
        if vuser:
            if const.sys_group_banned not in vuser.groups:
                vuser.groups.append(const.sys_group_banned)
                vuser.put()
        else:
            vuser = VUser()
            vuser.user = comment.author
            vuser.groups = [const.sys_group_banned]
            vuser.put()
            
        self.response.out.write('alert("User banned")')
        
class ModeratorPage_RecentComments(ModeratorRequestHandler):
    def get(self):
        super(ModeratorPage_RecentComments,self).get()
        start_index=0;
        if self.request.get('start'):
            start_index = int(self.request.get('start'))
            
        page_size = 10
        comments = VPageComment.all().order('-date').fetch(page_size+1, start_index)
        
        prev_page_url = None
        next_page_url = None
        
        if start_index>0:
            if start_index-page_size>0:
                prev_page_url = '/moderator/comments?start='+str(start_index-page_size)
            else:
                prev_page_url = '/moderator/comments'
                
        if len(comments)>page_size:
            next_page_url = '/moderator/comments?start='+str(start_index+page_size)
            comments = comments[:-1]
            
        template_values = {
                           'comments': comments,
                           'prev_page_url': prev_page_url,
                           'next_page_url': next_page_url
                           }
            
        self.write_template('html.core/moderator-recent-comments.html', template_values)

class ModeratorPage_BannedUsers(ModeratorRequestHandler):
    """Страница забанненых пользователей"""
    def get(self):
        super(ModeratorPage_BannedUsers,self).get()
        users = VUser.all().filter('groups =', const.sys_group_banned)
        template_values = {
                           'users': users
                           }
        self.write_template('html.core/moderator-banned-users.html', template_values)
        
class ModeratorAction_UserUnban(ModeratorRequestHandler):
    """Действие по разблокировке пользователя"""
    def get(self):
        super(ModeratorRequestHandler,self).get()
        user = VUser.get(self.request.get('key'))
        user.groups.remove(const.sys_group_banned)
        user.put()
        self.redirect('/moderator/bannedusers')