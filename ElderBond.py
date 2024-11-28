from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from DataBase import DataBaseAccess
import os
from PIL import Image

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Frontend Endpoints

@app.route('/')
def home():
    """Homepage showing all users and their content."""
    with DataBaseAccess() as db:
        users = db.get_all_users()
        content = db.get_all_posts()
    return render_template('index.html', users=users, content=content)


@app.route('/search_users', methods=['GET'])
def search_users():
    """Search for users by username or list all users."""
    username = request.args.get('username')
    with DataBaseAccess() as db:
        if username:
            db.cursor.execute("SELECT * FROM Users WHERE username LIKE ?", (f'%{username}%',))
            users = db.cursor.fetchall()
        else:
            users = db.get_all_users()
    return render_template('search_users.html', users=users, search_term=username)


@app.route('/delete_content/<int:content_id>', methods=['POST'])
def delete_content(content_id):
    """Delete a specific content post."""
    with DataBaseAccess() as db:
        db.delete_content(content_id)
    flash("Content deleted successfully!")
    return redirect(url_for('home'))


@app.route('/upload_post', methods=['GET', 'POST'])
def upload_post():
    """Upload a new post."""
    if request.method == 'POST':
        user_id = request.form['userId']
        title = request.form['title']
        text = request.form['text']
        image = request.files['image']

        # Save and process the image
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)

        # Resize and crop the image to 500x500px
        with Image.open(image_path) as img:
            img = img.resize((500, 500))
            img.save(image_path)

        with DataBaseAccess() as db:
            db.add_content(user_id, title, text, image_path)

        flash("Post uploaded successfully!")
        return redirect(url_for('home'))

    # Render the upload form
    with DataBaseAccess() as db:
        users = db.get_all_users()
    return render_template('upload_post.html', users=users)
