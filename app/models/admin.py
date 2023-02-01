from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import abort

from app.models.account import Controller

class UserAdminView(ModelView):
    column_display_pk = True


class MyAdminView(Controller, ModelView):
    template = 'admin/custom.html'
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.is_admin is True:
                return current_user.is_authenticated
            else:
                return abort(404)
            # return current_user.is_authenticated
        else:
            return abort(404)

    def not_auth(self):
        return "You are not authorized to view this page."
