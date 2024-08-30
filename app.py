from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
import bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
from models import db, User, File
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_tables():
    with app.app_context():
        db.create_all()

create_tables()  # Call this function to create tables

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login failed. Check your username and password.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    search_query = request.args.get('search', '')
    show_public = request.args.get('public', 'off') == 'on'
    show_private = request.args.get('private', 'off') == 'on'

    query = File.query

    if search_query:
        query = query.filter(File.filename.ilike(f'%{search_query}%'))

    if show_public and not show_private:
        query = query.filter_by(public=True)
    elif show_private and not show_public:
        query = query.filter_by(user_id=current_user.id)
    
    files = query.all()

    return render_template('index.html', files=files, show_public=show_public, show_private=show_private)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # Get new filename and public/private option from the form
            new_filename = request.form['filename']
            public = 'public' in request.form

            # Save the file
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(new_filename))
            file.save(filepath)
            
            # Get file size
            file_size = os.path.getsize(filepath)
            
            # Create a new File entry in the database
            new_file = File(
                filename=new_filename,
                filepath=filepath,
                user_id=current_user.id,
                public=public,
                size=file_size
            )
            db.session.add(new_file)
            db.session.commit()

            flash('File successfully uploaded')
            return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/download/<int:file_id>')
@login_required
def download_file(file_id):
    file = File.query.get(file_id)
    if file and (file.public or file.user_id == current_user.id):
        return send_from_directory(app.config['UPLOAD_FOLDER'], file.filename)
    else:
        flash('File not found or access denied')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
