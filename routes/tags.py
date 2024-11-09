from flask import render_template, request, redirect, url_for, session, flash, Blueprint, Response
from flask_login import login_required
import requests
from sqlalchemy import func
from sqlalchemy.orm import joinedload


from init import db
from models.link import Link, TagForm, Tag,link_tags, TagMergeForm,merge_tags, remove_tag
from models.user import User
from modules.filters import set_filter,get_filter,remove_filters
from modules.paging import items_per_page,get_paging_info


item_name = 'tag'
tag_bp = Blueprint(f'{item_name}s', __name__)


@login_required
@tag_bp.route ( '/tags', methods=['GET', 'POST'] )
def list():    
    paging = get_paging_info(count_tags())
    tags =get_tags(paging['page'])
    return render_template('tags.html', form=TagForm(), tags=tags, submit_label='Create',paging=paging, title='Tags')

@login_required
@tag_bp.route('/tags/delete/<int:tag_id>', methods=['GET'])
def tag_delete(tag_id):    
    tag = remove_tag(tag_id)
    if tag:
        flash(f'Removed tag {tag}','success')
    else: 
        flash(f'Failed to remove tag','fail')
    return redirect(url_for('.list'))

@login_required
@tag_bp.route('/tags/search')
def search():
    #todo do search
    return redirect(request.referrer)


@login_required
@tag_bp.route('/tags/removefilter/<filtertype>')
def remove_filter(filtertype):
    #todo remove search filter
    return redirect(request.referrer)

@login_required
@tag_bp.route('/tags/autocomplete/<prefix>')
def autocomplete(prefix):
    tags =  Tag.query.filter(Tag.name.ilike(f'{prefix}%')).order_by(Tag.count.desc()).all()
    return redirect(request.referrer, autotags=tags) 

@login_required
@tag_bp.route('/tags/edit/<int:tag_id>', methods=['GET','POST'])
def tag_edit(tag_id):
    tag = Tag.query.get(tag_id)    
    form = TagForm(obj=tag)
    
    if form.validate_on_submit():
        form.populate_obj(tag) 
        db.session.add(tag)
        db.session.commit()
        flash('Tag updated successfully.', 'success')
        return redirect(url_for('.list'))
    
    paging = get_paging_info(count_tags())
    tags = get_tags(paging['page'])  
    return render_template('tags.html', form=form, tag=tag, tags=tags, submit_label='Save',paging=paging, title='Tags')

@login_required
@tag_bp.route('/tags/merge/<int:tag_id>', methods=['GET','POST'])
def tag_merge(tag_id):
    tag = Tag.query.get(tag_id)    
    form = TagMergeForm(obj=tag)
    
    if form.validate_on_submit():        
        merge_to = form.merge_to.data
        merge_tags(tag_id,merge_to)
        flash(f'Merged from {tag.name} to {merge_to}', 'success')
        return redirect(url_for('.list'))
    
    paging = get_paging_info(count_tags())
    tags = get_tags(paging['page'])  
    return render_template('tags.html', form=form, tag=tag, tags=tags, submit_label='Merge',paging=paging, title='Tags')

def count_tags():
    return query_tags(True,session.get('user_id'),0)    

def get_tags(page):
    return query_tags(False,session.get('user_id'),page)

def query_tags(count,user_id,page):     
    search_filter=get_filter('links_search_filter')
    search_pattern=f'%{search_filter}%'
    
    query = Tag.query.filter(Tag.user_id==user_id)
    
    if search_filter:
        query = query.filter(Tag.name.ilike(search_pattern))

    if count:
        return query.count()
    else:         
        return query.order_by(Tag.count.desc()).offset((page - 1) * items_per_page).limit(items_per_page).all()

