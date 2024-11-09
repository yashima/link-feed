from datetime import datetime
from flask import session
import secrets
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField,ValidationError
from wtforms.validators import DataRequired, Length
from init import db
from urllib.parse import urlparse, quote, unquote
from sqlalchemy import func, select, and_
from sqlalchemy.orm import relationship, column_property

link_tags = db.Table('link_tags',
    db.Column('link_id', db.Integer, db.ForeignKey('link.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    domain = db.Column(db.String(200), nullable=False)
    url_path = db.Column(db.String(200))
    url_params = db.Column(db.String(200))
    summary = db.Column(db.String(512))
    comment = db.Column(db.String(512))    
    private = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    secret_link = db.Column(db.String(16), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author=db.Column(db.String(200))
    locale=db.Column(db.String(16))
    document_modified_at=db.Column(db.Date)
    canonical_link=db.Column(db.String(200))
    user = db.relationship('User', backref=db.backref('urls', lazy=True))
    tags = db.relationship('Tag', secondary=link_tags, backref=db.backref('links', lazy=True))

    __table_args__ = (
        db.UniqueConstraint('user_id', 'url_path', 'url_params', 'domain', name='_user_url_domain_uc'),
    )

    def __init__(self):
        self.secret_link = secrets.token_urlsafe(8)
        self.user_id=session.get("user_id")        

    def checkTags(self, tags,user_id):
        new_tags = []
        if not (tags is None or tags.strip() == ''):
            tag_names = [name.strip() for name in tags.split(',')]
            for tag_name in tag_names:
            
                tag = Tag.query.filter_by(name=tag_name, user_id=user_id).first()
                if tag:
                    new_tags.append(tag)
                else:
                    # Create a new tag if it doesn't exist
                    tag = Tag(name=tag_name, user_id=user_id)
                    db.session.add(tag)
                    new_tags.append(tag)
        
            db.session.commit()
        return new_tags

    def get_address(self):
        if not self.domain:
            return None
        return 'https://' + self.domain + ( self.url_path if self.url_path else '' ) + ( self.url_params if self.url_params else '' )

    def set_address(self, address):
        if not address:
            return

        address = unquote(address)
        if not address.startswith('http'):
            address = 'https://' + address        
        parsed_url = urlparse(address)
        self.domain = parsed_url.netloc
        #self.domain = self.domain.lstrip('www.')
        self.url_path = parsed_url.path
        self.url_params = address.replace(f"https://{self.domain}{self.url_path}", "")


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    private = db.Column(db.Boolean, default=False)
    organizational = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer)    
    count = column_property( select(func.count()).where(and_(link_tags.c.tag_id == id,link_tags.c.link_id==Link.id)).scalar_subquery())
    tagged_links = db.relationship('Link', 
        secondary=link_tags, 
        lazy='subquery',         
        backref=db.backref('tags_for_links', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('user_id', 'name', name='_user_tag_uc'),
    )

    def __str__(self):
        return self.name

    def to_dict(self):
        return { "id": self.id, "name": self.name, "user_id":self.user_id }

class TagForm(FlaskForm):
    name = StringField('Name', validators=[Length(max=100)])
    #parent = StringField('Parent', validators=[Length(max=100)])
    #private = BooleanField('Private')    
    #organizational = BooleanField('Organizational')

    def validate_name(self, field):
        name = field.data
        existing_tag = Tag.query.filter_by(name=name).first()
        if existing_tag:
            raise ValidationError('Tag already exists. Use merge to combine tags.')

    def populate_obj(self, obj):
        super().populate_obj(obj)
        #parent_tag = Tag.query.filter_by(name=self.parent.data,user_id=session.get('user_id')).first()
        #obj.parent_id = parent_tag.id

class TagMergeForm(FlaskForm):
    name = StringField('From', validators=[Length(max=100)])
    merge_to = StringField('To', validators=[Length(max=100),DataRequired()])
    
    def validate_merge_to(self, field):
        merge_to = field.data
        existing_tag = Tag.query.filter_by(name=merge_to).first()
        if not existing_tag:
            raise ValidationError('Tag does not exist. Use edit to rename tag.')
    
class LinkForm(FlaskForm):
    address = StringField('Link', validators=[DataRequired(), Length(max=400)],render_kw={"placeholder": "The Link you want to remember"})
    title = StringField('Title', validators=[Length(max=256)],render_kw={"placeholder": "Link Title, auto-fillable"})    
    author = StringField('Author', validators=[Length(max=100)],render_kw={"placeholder": "Link Author, auto-fillable... rarely"})        
    summary = TextAreaField('Summary', validators=[Length(max=512)],render_kw={"placeholder": "Summary, auto-fillable"})
    comment = TextAreaField('Comment', validators=[Length(max=512)],render_kw={"placeholder": "Your comment to this link"})
    tags_input = StringField('Tags', validators=[Length(max=256)],render_kw={"placeholder": "comma-separated tags"})
    private = BooleanField('Private')    

    def set_editing_mode(self, editing):
        self.address.render_kw = {'readonly': editing}

    def process(self, formdata=None, obj=None, **kwargs):
        super().process(formdata, obj, **kwargs)        
        if obj is not None:
            if not self.address.data:
                self.address.data = obj.get_address()
                self.tags_input.data = ', '.join(tag.name for tag in obj.tags) if obj.tags else ''

    def populate_obj(self, obj):
        super().populate_obj(obj)
        new_tags = obj.checkTags(self.tags_input.data, session.get("user_id"))
        obj.tags.clear();
        obj.tags.extend(new_tags)    
        obj.set_address(self.address.data)
        


def merge_tags(tag_remove_id, tag_keep_name):
    # Fetch the tags
    print('merge_tags')
    tag_remove = Tag.query.get(tag_remove_id)
    tag_keep = Tag.query.filter(Tag.name==tag_keep_name).first()
    
    if tag_remove is None or tag_keep is None:        
        return "One or both tags not found"

    # Assign all links of the tag to be removed to the tag to be kept
    for link in tag_remove.tagged_links:
        if link not in tag_keep.tagged_links:
            tag_keep.tagged_links.append(link)

    # Remove the tag
    tag_remove.tagged_links = []
    db.session.flush()    
    db.session.delete(tag_remove)
    db.session.commit()

def remove_tag(tag_id):
    # Fetch the tag
    tag = Tag.query.get(tag_id)
    
    if tag is None:
        return "Tag not found"

    # Disassociate the tag from all links
    tag.tagged_links = []

    # Remove the tag
    db.session.flush()    
    db.session.delete(tag)

    # Commit the changes
    db.session.commit()
    return tag.name


def remove_tag_mine(tag_id):
    tag = Tag.query.get(tag_id)
    links = Link.query.join(Link.tags).filter(Tag.id==tag_id).all()
    for link in links:
        link.tags.remove(tag)
    db.session.flush()
    db.session.refresh(tag)
    db.session.delete(tag)
    db.session.commit()
    return tag.name