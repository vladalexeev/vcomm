# -*- coding: utf-8 -*-

from base import ModeratorRequestHandler
from db.dbmodel import VPageComment

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