from flask import Flask, redirect, render_template, request, jsonify, send_from_directory, flash, url_for
from werkzeug.utils import secure_filename
import bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
from models import db, User, File
from config import Config
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

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


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('edit_profile'))

        # Hash the new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Update the user's password in the database
        current_user.password = hashed_password
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
    show_public = request.args.get('public', 'off') == 'on'
    show_private = request.args.get('private', 'off') == 'on'

    # Base query
    query = File.query

    if search_query:
        query = query.filter(File.filename.ilike(f'%{search_query}%'))

    if show_public and not show_private:
        # Show all public files
        query = query.filter(File.public == True)
    elif show_private and not show_public:
        # Show only the current user's private files
        query = query.filter(File.user_id == current_user.id)
    elif show_public and show_private:
        # Show all public files and current user's private files
        query = query.filter(
            (File.public == True) |
            (File.user_id == current_user.id)
        )

    files = query.all()

    file_list_html = render_template('file_list.html', files=files)
    return jsonify({'file_list': file_list_html})


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
            extension = original_filename.rsplit('.', 1)[1].lower()  # Extract file extension

            # Construct new filename with original extension
            new_filename_with_extension = f"{new_filename}.{extension}"
            file_path = os.path.join(UPLOAD_FOLDER, new_filename_with_extension)

            file.save(file_path)

            # Save file info to the database
            file_record = File(
                filename=new_filename_with_extension,
                filepath=file_path,  # Set the filepath
                user_id=current_user.id,
                public='public' in request.form,
                size=os.path.getsize(file_path)  # Get the file size
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



