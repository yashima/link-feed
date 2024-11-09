from flask import render_template, request, redirect, url_for, session, flash, Blueprint, Response, abort,make_response, send_file
from flask_login import login_required

#my stuff
from init import db
from modules.filters import get_filter, set_filter, remove_filters, remove_filter_list, set_filter_list, get_filter_list_ids
from modules.paging import items_per_page,get_paging_info
from modules.rssfeed import generate_feed
from models.link import Link, Tag
from models.user import User

social_bp = Blueprint('social', __name__)

@social_bp.route('/social', methods=['GET'])
def list():
    links = Link.query.filter(Link.private==False).order_by(Link.created_at.desc()).limit(50)
    return render_template('social.html', links=links)
