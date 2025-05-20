import os
from app import db
from app.forms import RegistrationForm, LoginForm, VideoUploadForm
from app.models import User, Video, Like, Dislike, Comment
from flask import render_template, redirect, url_for, flash, abort, jsonify, request
from flask_login import login_user, current_user, logout_user, login_required
from flask import Blueprint
import subprocess
import random
from werkzeug.utils import secure_filename
from datetime import datetime  
from sqlalchemy import func
from sqlalchemy.orm import joinedload

main_bp = Blueprint('main', __name__)

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
    'static', 
    'uploads'
)
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@main_bp.route('/')
def home():
    videos = Video.query.order_by(Video.created_at.desc()).all()
    return render_template('home.html', videos=videos)

@main_bp.route('/user/<username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_profile.html', user=user)

@main_bp.route('/library')
@login_required
def library():
    return render_template('videos.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            flash('Login failed. Check email and password', 'danger')
    return render_template('login.html', form=form)

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi'}

@main_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = VideoUploadForm()
    
    if form.validate_on_submit():
        try:
            video_file = form.video_file.data
            filename = secure_filename(video_file.filename)
            description=form.description.data,
            unique_name = f"{datetime.now().timestamp()}_{filename}"
            video_path = os.path.join(UPLOAD_FOLDER, unique_name)
            video_file.save(video_path)

            duration = get_video_duration(video_path)
            thumbnail_name = None
            
            for attempt in range(3):
                try:
                    random_time = random.uniform(1, max(2, duration - 3))
                    thumbnail_name = f"thumb_{unique_name.split('.')[0]}_{attempt}.jpg"
                    thumbnail_path = os.path.join(UPLOAD_FOLDER, thumbnail_name)
                    
                    subprocess.run([
                        'ffmpeg',
                        '-ss', str(random_time),
                        '-i', video_path,
                        '-vframes', '1',
                        '-q:v', '2',
                        thumbnail_path
                    ], check=True, timeout=10)
                    
                    if os.path.exists(thumbnail_path):
                        break
                except Exception as e:
                    print(f"Attempt {attempt+1} failed: {str(e)}")
                    thumbnail_name = None

            if not thumbnail_name or not os.path.exists(thumbnail_path):
                raise Exception("All thumbnail generation attempts failed")

            video = Video(
                title=form.title.data,
                filename=unique_name,
                thumbnail=thumbnail_name,
                duration=duration,
                user_id=current_user.id
            )
            db.session.add(video)
            db.session.commit()

            flash('Video uploaded successfully!', 'success')
            return redirect(url_for('main.home'))

        except Exception as e:
            db.session.rollback()
            print(f"Upload error: {str(e)}")
            flash('Error uploading video. Please try again.', 'danger')

    return render_template('upload.html', form=form)

@main_bp.route('/delete_video/<int:video_id>', methods=['POST','DELETE'])
@login_required
def delete_video(video_id):
    video = Video.query.get_or_404(video_id)
    
    if video.author != current_user:
        abort(403)
    
    try:
        video_path = os.path.join(UPLOAD_FOLDER, video.filename)
        thumb_path = os.path.join(UPLOAD_FOLDER, video.thumbnail)
        
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
        
        db.session.delete(video)
        db.session.commit()
        flash('Видео успешно удалено', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении видео', 'danger')
        print(f"Delete error: {str(e)}")

    return redirect(url_for('main.home'))

@main_bp.route('/video/<int:video_id>')
def video(video_id):
    video = Video.query.options(
        joinedload(Video.video_comments)
          .joinedload(Comment.comment_author)
    ).get_or_404(video_id)
    return render_template('video.html', video=video)

@main_bp.route('/videos')
def videos():
    all_videos = Video.query.order_by(Video.created_at.desc()).all()
    return render_template('videos.html', videos=all_videos)

@main_bp.route('/all-videos') 
def all_videos():             
    all_videos = Video.query.order_by(Video.created_at.desc()).all()
    return render_template('videos.html', videos=all_videos)

def get_video_duration(video_path):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
         '-of', 'default=noprint_wrappers=1:nokey=1', video_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return float(result.stdout)

@main_bp.route('/like/<int:video_id>', methods=['POST'])
@login_required
def like_video(video_id):
    video = Video.query.get_or_404(video_id)
    existing = Like.query.filter_by(user_id=current_user.id, video_id=video.id).first()

    if existing:
        db.session.delete(existing)
        status = 'unliked'
    else:
        db.session.add(Like(user_id=current_user.id, video_id=video.id))
        status = 'liked'

    db.session.commit()

    likes_count = Like.query.filter_by(video_id=video.id).count()

    return jsonify({
        'status': status,      
        'count': likes_count    
    })

@main_bp.route('/dislike/<int:video_id>', methods=['POST'])
@login_required
def dislike_video(video_id):
    video = Video.query.get_or_404(video_id)
    like = Like.query.filter_by(user_id=current_user.id, video_id=video.id).first()
    dislike = Dislike.query.filter_by(user_id=current_user.id, video_id=video.id).first()
    
    if like:
        db.session.delete(like)
        status = 'unliked'
    else:
        new_like = Like(user_id=current_user.id, video_id=video.id)
        db.session.add(new_like)
        status = 'liked'
    db.session.commit()

    likes_count = Like.query.filter_by(video_id=video.id).count()
    return jsonify({
        'status': status,
        'likes': likes_count
    })

@main_bp.route('/comment/<int:video_id>', methods=['POST'])
@login_required
def add_comment(video_id):
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    comment = Comment(
        text=data['text'],
        user_id=current_user.id,
        video_id=video_id
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify({
        'id': comment.id,
        'text': comment.text,
        'author': current_user.username,
        'avatar': current_user.avatar,
        'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
    }), 201

@main_bp.route('/subscribe/<int:author_id>', methods=['POST'])
@login_required
def subscribe(author_id):
    author = User.query.get_or_404(author_id)
    if current_user.id == author.id:
        return jsonify({'status': 'error', 'message': 'Нельзя подписаться на себя'}), 400

    if current_user.subscribed.filter_by(id=author.id).first():
        current_user.subscribed.remove(author)
        db.session.commit()
        return jsonify({'status': 'unsubscribed'})
    else:
        current_user.subscribed.append(author)
        db.session.commit()
        return jsonify({'status': 'subscribed'})
