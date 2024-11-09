from flask import request, redirect, url_for, session, render_template
from init import create_app
import os

app=create_app()


@app.errorhandler(500)  # Customize the error code as needed
def error_500(error):
    message = "Something went really really wrong inside the server. Please try again later."
    return render_template("error.html", error_message=message), 500

@app.errorhandler(404)  # Customize the error code as needed
def error_404(error):
    message = "The requested page was not found."
    return render_template("error.html", error_message=message), 404



@app.template_filter('strftime')
def format_datetime(value, dateformat='%Y-%m-%d %H:%M:%S'):
    if value is None:
        return ''
    return value.strftime(dateformat)

@app.before_request
def require_login():
    allowed_routes = ['auth.login', 'auth.register', 'static', 'links.permalink', 'links.links_rss','links.public_links','links.share_tag']  # define routes that are allowed without logging in
    if 'username' not in session and request.endpoint not in allowed_routes:
        return redirect(url_for('auth.login'))

if __name__ == '__main__':
    # switch between run/manager based on your need.
    # manager.run() # for DB migration    
    if os.environ.get('MODE')=='development' :
        app.run(threaded=True, debug=True)
    else:
        app.run(host='0.0.0.0', port=5000,debug=True,threaded=True)
