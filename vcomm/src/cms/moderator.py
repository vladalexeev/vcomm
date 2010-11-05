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
        page = comment.page_ref
        VPageComment.delete(comment)
        if self.request.get('return') == 'page':
            self.redirect('/page/'+page.name)

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
        page = comment.page_ref
        if return_target == 'page':
            self.redirect('/page/'+page.name)
            
class ModeratorAction_CommentUserBan(ModeratorRequestHandler):
    def get(self):
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
