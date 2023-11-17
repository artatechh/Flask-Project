from flask import render_template, Blueprint

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(404)
def error404(error):
    return render_template('error404.html', title='NOT FOUND'), 404


@errors.app_errorhandler(403)
def error403(error):
    return render_template('error403.html', title='Permission'), 404


@errors.app_errorhandler(500)
def error500(error):
    return render_template('error500.html', title='Wrong🤐'), 500