from flask import render_template
from app import app, db

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'),404

# 数据库调用出错
@app.errorhandler(500)
def not_found_error(error):
    db.session().rollback()
    return render_template('500.html'),500
