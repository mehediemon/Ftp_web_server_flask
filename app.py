from flask import Flask, redirect, render_template, request, flash, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
from models import db, User, File
from config import Config
from werkzeug.utils import secure_filename
from math import ceil

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

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3', 'docx', 'xlsx'}

def create_tables():
    with app.app_context():
        db.create_all()

create_tables()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Create a new user
        new_user = User(username=username)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()

        flash('User registered successfully!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login failed. Check your username and password.', 'danger')
    return render_template('login.html')


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('edit_profile'))

        # Update the user's password in the database
        current_user.set_password(new_password)
        db.session.commit()

        flash('Password updated successfully', 'success')
        return redirect(url_for('index'))

    return render_template('edit_profile.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/file_list')
@login_required
def file_list():
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 10  # Number of files per page

    # Construct query with filtering and searching
    query = File.query.filter(File.filename.ilike(f'%{search_query}%'))
    
    if request.args.get('public'):
        query = query.filter_by(public=True)
    if request.args.get('private'):
        query = query.filter_by(public=False, user_id=current_user.id)
    
    # Pagination
    files = query.order_by(File.upload_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    total_pages = files.pages  # Get total pages from the pagination object

    return render_template('file_list.html', files=files.items, total_pages=total_pages, current_page=page, search_query=search_query)



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_file', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        new_filename = request.form.get('filename', '')

        if file and allowed_file(file.filename):
            original_filename = secure_filename(file.filename)
            extension = original_filename.rsplit('.', 1)[1].lower()

            new_filename_with_extension = f"{new_filename}.{extension}"
            file_path = os.path.join(UPLOAD_FOLDER, new_filename_with_extension)

            file.save(file_path)

            file_record = File(
                filename=new_filename_with_extension,
                size=os.path.getsize(file_path),
                user_id=current_user.id,
                public='public' in request.form
            )
            db.session.add(file_record)
            db.session.commit()

            flash('File uploaded successfully', 'success')
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
