from flask import Flask, request, jsonify, make_response, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, BigInteger, select, func
from sqlalchemy.orm import relationship
from sqlalchemy import Index
import logging
from flask_cors import CORS
from flask_session import Session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from datetime import datetime
import re
from flask_login import current_user
import os
import random

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
if os.environ.get('FLASK_ENV') != 'production':
    app.config['CORS_HEADERS'] = 'Content-Type'
    CORS(app, supports_credentials=True, origins=["http://localhost:3000"])
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///annotations.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
    

db = SQLAlchemy(app)
app.secret_key = 'moggablogg'

app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' #'None' if os.environ.get('FLASK_ENV') == 'production' else 'Lax'
app.config['REMEMBER_COOKIE_DURATION'] = 24*3600  # or any other duration in seconds
app.config['SESSION_TYPE'] = 'filesystem'  # or 'redis', 'memcached', etc.
app.config['SESSION_PERMANENT'] = True
Session(app)

login_manager = LoginManager()
login_manager.init_app(app)

class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    id = Column(BigInteger, primary_key=True)
    title = Column(String, nullable=False)
    text = Column(String, nullable=False)
    site_name = Column(String, nullable=False)
    link = Column(String, nullable=False, unique=True)
    comments = relationship("Comment", backref="blog_post")

class Comment(db.Model):
    __tablename__ = 'comments'
    id = Column(BigInteger, primary_key=True)
    body = Column(String, nullable=False)
    signature = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    blog_post_id = Column(BigInteger, ForeignKey('blog_posts.id'), nullable=False)

    __table_args__ = (
        Index('ix_comments_blog_post_id', 'blog_post_id'),
        Index('ix_comments_created_at', 'created_at'),
    )

class Annotator(db.Model, UserMixin):
    __tablename__ = 'annotators'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    annotations_count = Column(BigInteger, default=0)

class Annotation(db.Model):
    __tablename__ = 'annotations'
    id = Column(BigInteger, primary_key=True)
    comment_id = Column(BigInteger, db.ForeignKey('comments.id'), nullable=False)
    annotator_id = Column(BigInteger, db.ForeignKey('annotators.id'), nullable=False)
    annotator = relationship("Annotator", backref="annotations")
    label = Column(String(50), nullable=False)
    task_type = Column(String(50), nullable=False)
    show_blog_post = Column(db.Boolean, default=False)
    show_preceding_comments = Column(db.Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Annotator, int(user_id))

@app.route('/register', methods=['POST'])
def register_annotator():
    data = request.json
    name = data.get('name')
    password = data.get('password')

    if Annotator.query.filter_by(name=name).first() is not None:
        return jsonify({'message': 'Annotator already exists'}), 400

    hashed_password = generate_password_hash(password)
    new_annotator = Annotator(name=name, password_hash=hashed_password)
    db.session.add(new_annotator)
    db.session.commit()

    return jsonify({'message': 'Registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login_annotator():
    try:
        data = request.json
        name = data.get('name')
        password = data.get('password')

        annotator = Annotator.query.filter_by(name=name).first()
        if annotator and check_password_hash(annotator.password_hash, password):
            login_user(annotator)  # Use flask_login's login_user
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'message': 'Invalid username or password'}), 401
    except Exception as e:
        app.logger.error(f'An error occurred during login: {e}')
        return jsonify({'message': 'Internal Server Error'}), 500
    
@app.route('/is_logged_in', methods=['GET'])
def is_logged_in():
    if current_user.is_authenticated:
        return jsonify({'logged_in': True, 'username': current_user.name}), 200
    else:
        return jsonify({'logged_in': False}), 200

@app.route('/logout', methods=['POST'])
@login_required  # Protect this route
def logout_annotator():
    logout_user()  # Use flask_login's logout_user
    return jsonify({'message': 'Logged out successfully'}), 200

def get_blog_and_preceding_comments(comment):
    # Fetch the blog post
    #blog_post = BlogPost.query.get(comment.blog_post_id)
    blog_post = db.session.get(BlogPost, comment.blog_post_id)
    blog_post_data = {
        'id': blog_post.id,
        'title': blog_post.title,
        'text': blog_post.text,
        'site_name': blog_post.site_name,
        'link': blog_post.link
    }
    
    # Fetch all comments for the blog post
    all_comments = Comment.query.filter(
        Comment.blog_post_id == comment.blog_post_id
    ).all()

    # Filter comments that were created before the current comment
    preceding_comments = [c for c in all_comments if c.created_at < comment.created_at]

    # Sort the filtered comments by their creation datetime
    preceding_comments.sort(key=lambda x: x.created_at)

    # Serialize preceding comments
    preceding_comments_data = [
        {'id': c.id, 'text': c.body, 'signature': c.signature}
        for c in preceding_comments
    ]
    return blog_post_data, preceding_comments_data

@app.route('/annotate', methods=['GET'])
def get_annotation():
    task_type = request.args.get('task_type')
    current_comment_id = request.args.get('current_comment_id', type=int)
    direction = request.args.get('direction', type=int, default=0) # +1 for next, -1 for previous

    app.logger.debug(f"task_type: {task_type}, current_comment_id: {current_comment_id}, direction: {direction}")

    # Fetch the next or previous comment based on direction
    comment = None  # Initialize comment to None
    comment_query = Comment.query.order_by(Comment.id)
    if direction == 1:
        comment = comment_query.filter(Comment.id > current_comment_id).first()
    elif direction == -1:
        comment = Comment.query.filter(Comment.id < current_comment_id).order_by(Comment.id.desc()).first()
        if comment is None:
            # If it's the first comment, return it instead of returning nothing
            comment = Comment.query.order_by(Comment.id).first()
            app.logger.debug(f"First comment with id: {comment.id} is returned")
        else:
            app.logger.debug(f"Found previous comment with id: {comment.id}")
    else:
        comment = comment_query.filter(Comment.id == current_comment_id).first()

    if comment:
        blog_post_data, preceding_comments_data = get_blog_and_preceding_comments(comment)
        return jsonify({
            'comment_id': str(comment.id),
            'text': comment.body,
            'signature': comment.signature,
            'preceding_comments': preceding_comments_data,
            'blog_post': blog_post_data
        }), 200
    else:
        app.logger.debug("No more comments available")
        return jsonify({'message': 'No more comments available'}), 404

@app.route('/annotate', methods=['POST'])
@login_required
def annotate():
    data = request.json
    comment_id = data.get('comment_id')
    # Get annotator_name from session
    annotator_name = data.get('user')
    label = data.get('labels')
    if isinstance(label, list):
        label = ';'.join(label)
    task_type = data.get('task')
    comment_id = data.get('commentId')
    show_blog_post = data.get('additionalData', {}).get('showBlogPost', False)
    show_preceding_comments = data.get('additionalData', {}).get('showPrecedingComments', False)

    #print(f"comment_id: {comment_id}, annotator_name: {annotator_name}, label: {label}, task_type: {task_type}")

    annotator = Annotator.query.filter_by(name=annotator_name).first()
    if annotator is None:
        return jsonify({'message': 'Annotator not found'}), 404

    new_annotation = Annotation(
        comment_id=comment_id,
        annotator_id=annotator.id,
        label=label,
        task_type=task_type,
        show_blog_post=show_blog_post,  # Save new data
        show_preceding_comments=show_preceding_comments,  # Save new data
    )
    annotator.annotations_count += 1
    db.session.add(new_annotation)
    db.session.commit()

    return jsonify({'message': 'Annotation added successfully'}), 201

@app.route('/annotate/previous_unannotated', methods=['GET'])
def get_previous_unannotated_comment():
    task_type = request.args.get('task_type')
    
    current_comment_id = request.args.get('current_comment_id', type=int)
    
    if not task_type:
        return jsonify({'message': 'Task type is required'}), 400

    # Find the closest previous comment that has not been annotated for the selected task
    subquery = select(Annotation.comment_id).filter(Annotation.task_type == task_type).subquery()
    comment = Comment.query.filter(Comment.id < current_comment_id, ~Comment.id.in_(subquery)).order_by(Comment.id.desc()).first()

    if comment:
        blog_post_data, preceding_comments_data = get_blog_and_preceding_comments(comment)
        return jsonify({
            'comment_id': str(comment.id),
            'text': comment.body,
            'signature': comment.signature,
            'preceding_comments': preceding_comments_data,
            'blog_post': blog_post_data
        }), 200
    else:
        # If no unannotated comment is found, return the first comment
        first_comment = Comment.query.order_by(Comment.id).first()
        if first_comment:
            blog_post_data, preceding_comments_data = get_blog_and_preceding_comments(first_comment)
            return jsonify({
                'comment_id': str(first_comment.id),
                'text': first_comment.body,
                'signature': first_comment.signature,
                'preceding_comments': preceding_comments_data,
                'blog_post': blog_post_data
            }), 200
        else:
            return jsonify({'message': 'No comments available'}), 404

@app.route('/annotate/next_unannotated', methods=['GET'])
def get_next_unannotated_comment():
    task_type = request.args.get('task_type')
    current_comment_id = request.args.get('current_comment_id', type=int, default=None)

    if not task_type:
        return jsonify({'message': 'Task type is required'}), 400

    # Find the closest next comment that has not been annotated for the selected task
    subquery = select(Annotation.comment_id).filter(Annotation.task_type == task_type).subquery()
    # Use the subquery within an IN clause without warning
    query = Comment.query.filter(~Comment.id.in_(subquery)).order_by(Comment.id)
    
    if current_comment_id is not None:
        query = query.filter(Comment.id > current_comment_id)
    comment = query.first()

    if comment:
        blog_post_data, preceding_comments_data = get_blog_and_preceding_comments(comment)
        return jsonify({
            'comment_id': str(comment.id),
            'text': comment.body,
            'signature': comment.signature,
            'preceding_comments': preceding_comments_data,
            'blog_post': blog_post_data
        }), 200
    else:
        return jsonify({'message': 'No unannotated comments available'}), 404

@app.route('/annotate/next_submit_unannotated', methods=['GET'])
def get_next_submit_unannotated_comment():
    if random.random() < 0.5:
        return get_next_unannotated_comment()
    task_type = request.args.get('task_type')
    current_comment_id = request.args.get('current_comment_id', type=int, default=None)

    if not task_type:
        return jsonify({'message': 'Task type is required'}), 400

    #print("YAY!")

    current_user_id = current_user.get_id()
    if current_user_id:
        subquery = (
            select(Annotation.comment_id)
            .filter_by(task_type=task_type)
            .group_by(Annotation.comment_id)
            .having(func.count(Annotation.comment_id) == 1)
            .alias()
        )

        exclude_user_subquery = (
            select(Annotation.comment_id)
            .join(Annotator)
            .filter(Annotator.id == current_user_id)
            .alias()
        )

        query = (
            select(Comment)
            .where(Comment.id.in_(select(subquery.c.comment_id)))
            .where(~Comment.id.in_(select(exclude_user_subquery.c.comment_id)))
            .order_by(func.random())
        )

        comment = db.session.execute(query).scalars().first()
    else:
        comment = None

    if not comment:
        return get_next_unannotated_comment()

    if comment:
        blog_post_data, preceding_comments_data = get_blog_and_preceding_comments(comment)
        return jsonify({
            'comment_id': str(comment.id),
            'text': comment.body,
            'signature': comment.signature,
            'preceding_comments': preceding_comments_data,
            'blog_post': blog_post_data
        }), 200
    else:
        return jsonify({'message': 'No unannotated comments available'}), 404

@app.route('/cleanup_test_data', methods=['POST'])
def cleanup_test_data():
    data = request.json
    annotator_name = data.get('annotator_name')

    annotator = Annotator.query.filter_by(name=annotator_name).first()
    if annotator:
        # Delete annotations made by the test user
        annotations = Annotation.query.filter_by(annotator_id=annotator.id).all()
        for annotation in annotations:
            db.session.delete(annotation)

        # Finally, delete the test user
        db.session.delete(annotator)
        db.session.commit()
        return jsonify({'message': 'Test data cleaned up successfully'}), 200
    else:
        return jsonify({'message': 'Annotator not found'}), 404

@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    annotators = Annotator.query.order_by(Annotator.annotations_count.desc()).all()
    leaderboard_data = [{'name': annotator.name, 'annotations': annotator.annotations_count} for annotator in annotators]

    return jsonify(leaderboard_data), 200

@app.route('/user_task_counts', methods=['GET'])
@login_required
def user_task_counts():
    # Get the current logged-in user's ID
    annotator_id = current_user.id

    # Construct the query using select()
    task_counts_query = select(
        Annotation.task_type,
        func.count(Annotation.comment_id.distinct()).label('count')
    ).where(
        Annotation.annotator_id == annotator_id
    ).group_by(
        Annotation.task_type
    )

    # Execute the query and fetch all results
    task_counts = db.session.execute(task_counts_query).all()

    # Convert query result to a dictionary for easier JSON serialization
    task_counts_dict = {task_type: count for task_type, count in task_counts}

    return jsonify(task_counts_dict), 200

@app.route('/comment/<path:subpath>')
def handle_comment(subpath):
    """
    Serve index.html for paths under /comment, allowing React to handle routing.
    The <path:subpath> captures any text after /comment/ as a variable, but we don't
    need to use it directly since we always serve index.html for these routes.
    """
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    context = ('cert.pem', 'key.pem')
    with app.app_context():
        db.create_all()
    app.run(ssl_context=context)
