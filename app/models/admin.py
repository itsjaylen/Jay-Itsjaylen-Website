from flask_admin.contrib.sqla import ModelView

class UserAdminView(ModelView):
    column_display_pk = True