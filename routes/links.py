from flask import render_template, request, redirect, url_for, session, flash, Blueprint, Response, abort,make_response, send_file
from flask_login import login_required
import re
from sqlalchemy import or_, func
from sqlalchemy.exc import IntegrityError

#my stuff
from init import db
from modules.filters import get_filter, set_filter, remove_filters, remove_filter_list, set_filter_list, get_filter_list_ids
from modules.paging import items_per_page,get_paging_info
from modules.rssfeed import generate_feed
from models.link import Link, LinkForm, Tag
from models.user import User
from models.usersettings import UserSetting, lookup_setting
from modules.exports import generate_pdf
from modules.metadata import update_meta_data, get_website_title

link_bp = Blueprint('links', __name__)

@link_bp.route('/links', methods=['GET'])
def list():
    user_id= session.get('_user_id')    
    return redirect(url_for('.list_user',page_user_id=user_id))

@login_required
@link_bp.route('/links/<int:page_user_id>', methods=['GET','POST'])
def list_user(page_user_id):        
    paging = get_paging_info(count_links(page_user_id))
    links = get_links(page_user_id,paging['page'])
    form = LinkForm()

    if form.validate_on_submit():
        link = Link()
        form.populate_obj(link)
        if not link.title:
            link.title= get_website_title(form.address.data)
        db.session.add(link)
        db.session.commit()
        return redirect(url_for('.list'))
    
    page_user_secret = User.query.get(page_user_id).user_secret
    return render_template('links.html', form=form,page_user_id=page_user_id,links=links,paging=paging,page_user_secret=page_user_secret,filter_tags=get_filter_tags())

@link_bp.route('/links/<user_secret>', methods=['GET'])
def public_links(user_secret):
    user = User.query.filter_by(user_secret=user_secret).first()
    filters = {"private_filter" : False }
    paging = get_paging_info(count_links_with_filter(user.id,filters))
    links = get_linkes_with_filter(user.id,paging['page'],filters)
    return render_template('public_links.html', links=links,user_secret=user.id,paging=paging)

@link_bp.route('/links/<user_secret>/<tag>')
def share_tag(user_secret, tag):    
    user = User.query.filter_by(user_secret=user_secret).first()
    filters = {"tag_name_filter":tag, "private_filter" : False }
    paging = get_paging_info(count_links_with_filter(user.id,filters))
    links = get_linkes_with_filter(user.id,paging['page'],filters)
    return render_template('public_links.html', links=links,user_secret=user.id,paging=paging)

@login_required
@link_bp.route('/links/add', methods=['POST','GET'])
def add_link():
    url = request.args.get('url')
    local = request.args.get('local')
    print(f'local={local}')
    link=Link()
    redirect_flag=0
    if url:        
        link.set_address(url)
        update_meta_data(link)
        try: 
            db.session.add(link)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            if "UNIQUE constraint failed" in str(e):
                error_message = "A record with the same unique value already exists."
            else:
                error_message = "An error occurred while saving the record."            
            return render_template('error.html',error_message=error_message)
        redirect_flag=1 if not local else 0
    return redirect(url_for('.edit_link',link_id=link.id if link.id else 0, redirect_flag=redirect_flag))

@login_required
@link_bp.route('/links/edit/<int:link_id>', methods=['GET', 'POST'])
def edit_link(link_id):
    page_user_id=session.get('user_id')
    paging = get_paging_info(count_links(page_user_id))
    links = get_links(page_user_id,paging['page'])        
    redirect_arg = request.args.get('redirect_flag')
    redirect_flag = int(redirect_arg if redirect_arg is not None else 0)        
    redirect_address = url_for('.list')    

    link = Link.query.get(link_id)
    if not link:
        link = Link()
    elif redirect_flag==1:
        redirect_address = link.get_address() 
    form = LinkForm(obj=link)    
    
    if form.validate_on_submit():       
        form.populate_obj(link) 
        db.session.add(link)
        db.session.commit()                
        print(f'next up {redirect_address}')
        return redirect(redirect_address)

    page_user_secret = User.query.get(page_user_id).user_secret
    return render_template('links.html', links=links, form=form, link=link,page_user_id=page_user_id,page_user_secret=page_user_secret,paging=paging)

@login_required
@link_bp.route('/links/delete/<int:link_id>', methods=['GET'])
def delete_link(link_id):
    print('doing something')
    link = Link.query.get_or_404(link_id)    
    db.session.delete(link)
    db.session.commit()
    flash('Link deleted successfully', 'success')
    return redirect(request.referrer)



@link_bp.route('/links/s/<secret_link>')
def permalink(secret_link):
    link = Link.query.filter_by(secret_link=secret_link).first()
    if link:
        return render_template('link.html', link=link)
    else:
        # Handle the case when the link with the provided secret_link is not found
        return "Link not found"

@link_bp.route('/links/<user_secret>/rss.xml', methods=['GET'])
def links_rss(user_secret):
    user = User.query.filter_by(user_secret=user_secret).first()
    print(f'getting rss for user={user}')
    links = Link.query.filter_by(user_id=user.id, private=False).order_by(Link.created_at.desc()).limit(25).all()    
    feed = generate_feed(user.username, links)

    # Return the RSS feed as a response with the appropriate content type
    return Response(feed, mimetype='application/rss+xml')    

@login_required
@link_bp.route('/links/export')
def download_links():
    query = Link.query.filter(Link.user_id==session.get('user_id'))
    query = add_filters_to_query(query, loadFilterDict())
    links = query.order_by(Link.created_at.desc()).all()
    return generate_pdf(links)


@login_required
@link_bp.route('/links/filter/private/<int:link_id>')
def filter_private(link_id):
    link = Link.query.filter_by(id=link_id).first()
    set_filter('links_private_filter',link.private)
    return redirect(url_for('.list'))

@login_required
@link_bp.route('/links/filter/domain/<int:link_id>')
def filter_domain(link_id):
    link = Link.query.filter_by(id=link_id).first()
    set_filter('links_domain_filter',link.domain.lstrip('www.'))
    return redirect(url_for('.list'))

@login_required
@link_bp.route('/links/filter/tag/<int:tag_id>')
def filter_tag(tag_id):
    tag = Tag.query.get(tag_id);
    set_filter_list('links_tag_filter',tag)    
    return redirect(url_for('.list'))

@login_required
@link_bp.route('/links/search')
def search():
    query = request.args.get('q')
    #todo sanitize input to contain only allowed characters for search
    session['links_search_filter']=query
    print(f'search query={query}')
    return redirect(url_for('.list'))

@login_required
@link_bp.route('/links/filter/remove/<filtertype>')
def remove_filter(filtertype):
    set_filter(filtertype, None)
    return redirect(url_for('.list'))

@login_required
@link_bp.route('/links/filter/remove/<filtertype>/<int:tag_id>')
def remove_filter_tag(filtertype, tag_id):
    tag = Tag.query.get(tag_id);
    remove_filter_list(filtertype,tag)
    return redirect(url_for('.list'))

@login_required
@link_bp.route('/links/filter/remove/')
def remove_all_filters():
    remove_filters(['links_domain_filter','links_private_filter','links_tag_filter','links_search_filter'])
    return redirect(url_for('.list'))

@login_required
@link_bp.route('/links/fetchmeta/<int:link_id>')
def fetch_meta(link_id):
    link = Link.query.filter_by(id=link_id).first()
    update_meta_data(link)
    db.session.add(link)
    db.session.commit()
    return redirect(request.referrer)

def count_links(page_user_id):
    return query_links(True,page_user_id,0, loadFilterDict())    

def count_links_with_filter(page_user_id,filters):
    return query_links(True,page_user_id,0, filters)    

def get_linkes_with_filter(page_user_id,page, filters):
    return query_links(False,page_user_id,page, filters)

def get_links(page_user_id,page):
    return query_links(False,page_user_id,page,loadFilterDict())

def loadFilterDict():
    filters = {
        "private_filter" : get_filter('links_private_filter'),
        "domain_filter" : get_filter('links_domain_filter'),
        "tag_filter" : get_filter_list_ids('links_tag_filter'),
        "search_filter": get_filter('links_search_filter')
    }
    return filters


def query_links(count,page_user_id,page,filters):     
   
    query = Link.query.filter(Link.user_id==page_user_id)
    
    if not page_user_id==session.get('user_id'):
        query = query.filter(Link.private == False)

    query = add_filters_to_query(query,filters)

    if count:
        return query.count()
    else: 
        return query.order_by(Link.created_at.desc()).offset((page - 1) * items_per_page).limit(items_per_page).all()

def add_filters_to_query(query, filters):
    search_pattern =f'%{filters.get("search_filter")}%'
    if filters.get("private_filter") is not None:
        query = query.filter(Link.private==filters.get("private_filter"))

    if filters.get("domain_filter"):
        query = query.filter(Link.domain.ilike(f'%{filters.get("domain_filter")}'))

    if filters.get("tag_filter"):
        tag_filters = filters.get("tag_filter")
        query = query.join(Link.tags).filter(Tag.id.in_(tag_filters)).group_by(Link.id).having(func.count('*')==len(tag_filters))

    if filters.get("tag_name_filter"):
        query = query.join(Link.tags).filter(Tag.name == filters.get("tag_name_filter"))

    if filters.get("search_filter"):
        query = query.join(Link.tags).filter(or_(
            Link.title.ilike(search_pattern), 
            Link.comment.ilike(search_pattern),
            Link.domain.ilike(search_pattern),
            Tag.name.ilike(search_pattern)))
    return query;



def get_filter_tags():
    filters = session.get('links_tag_filter')
    if filters and len(filters)>0 :
        return Tag.query.filter(Tag.id.in_(filters)).all()
    else:
        return []