from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
import random

subscriptions = db.Table(
    'subscriptions',
    db.Column('subscriber_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('author_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    avatar = db.Column(db.String(64), default='images/avatar.png')
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    likes = db.relationship('Like', backref='video', lazy=True)
    dislikes = db.relationship('Dislike', backref='video', lazy=True)
    comments = db.relationship('Comment', backref='video', lazy=True)

    subscribed = db.relationship(
        'User',
        secondary=subscriptions,
        primaryjoin=(subscriptions.c.subscriber_id == id),
        secondaryjoin=(subscriptions.c.author_id == id),
        backref=db.backref('subscribers', lazy='dynamic'),
        lazy='dynamic'
    )

    videos = db.relationship(
        'Video', 
        back_populates='author',
        cascade='all, delete-orphan',
        lazy=True
    )

    likes = db.relationship(
        'Like',
        foreign_keys='Like.user_id',
        back_populates='user',
        lazy='dynamic'
    )

    user_comments = db.relationship(
        'Comment', 
        back_populates='comment_author',
        foreign_keys='Comment.user_id',
        lazy='dynamic' 
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader 
def load_user(id):
    return User.query.get(int(id))

class Like(db.Model):
    __tablename__ = 'like'
    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=True)
    
    __table_args__ = (
        db.CheckConstraint(
            '(comment_id IS NOT NULL AND video_id IS NULL) OR (comment_id IS NULL AND video_id IS NOT NULL)',
            name='check_like_target'
        ),
    )

    user = db.relationship(
        'User',
        back_populates='likes',
        foreign_keys=[user_id]
    )
    video = db.relationship(
        'Video',
        back_populates='likes',
        foreign_keys=[video_id]
    )


class Dislike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    
    parent_video = db.relationship(
        'Video', 
        back_populates='video_comments',
        foreign_keys=[video_id]
    )
    
    comment_author = db.relationship(
        'User', 
        back_populates='user_comments',
        foreign_keys=[user_id]
    )

class Video(db.Model):
    __tablename__ = 'video'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=False, default='')
    filename = db.Column(db.String(100))
    thumbnail = db.Column(db.String(100), default='default-thumbnail.jpg') 
    duration = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author  = db.relationship('User', back_populates='videos')

    video_comments = db.relationship(
        'Comment',
        back_populates='parent_video',
        foreign_keys='Comment.video_id',
        cascade='all, delete-orphan',
        lazy='select'
    )

    likes = db.relationship(
        'Like',
        foreign_keys='Like.video_id',
        back_populates='video',
        lazy='dynamic'
    )


