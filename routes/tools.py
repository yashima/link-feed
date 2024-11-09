from flask import render_template, request, redirect, url_for, session, flash, Blueprint
from flask_login import login_required

tools_bp = Blueprint('tools', __name__)

@login_required
@tools_bp.route('/tools')
def tools():
    return render_template('tools.html')

