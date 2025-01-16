from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
import os
from DataBase import DataBaseAcess
import pika
import json

app = Flask(__name__)

# Flask environment configuration
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')
app.config['SQLITE_DB_PATH'] = os.getenv('SQLITE_DB_PATH', 'social_media.db')
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')  # Use environment variable for production
bcrypt = Bcrypt(app)

# Database initialization
db = DataBaseAcess()

# Directory for uploaded images
UPLOAD_FOLDER = os.path.join('static', 'images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Home Route ---
@app.route('/')
def home():
    if "user_id" in session:
        users = db.get_all_users()
        content = db.get_all_content()
        return render_template('main_page.html', users=users, content=content, logged_in=True)

    return redirect(url_for('login'))

# --- Login Route ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login an existing user."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = db.get_user_by_email(email)

        if user and bcrypt.check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            users = db.get_all_users()
            content = db.get_all_content()
            return render_template('main_page.html', users=users, content=content, logged_in=True)
        else:
            flash('Invalid email or password.')
    return render_template('login.html')

# --- Signup Route ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Sign up a new user."""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        try:
            db.insert_user(username, email, password)
            flash('Account created successfully! Please log in.')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Error: {str(e)}")
    return render_template('signup.html')

# --- Logout Route ---
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- User Posts Route ---
@app.route('/account', methods=['GET'])
def user_account():
    """Display the posts of the currently logged-in user."""
    if "user_id" in session:
        user_id = session['user_id']
        user_content = db.get_content_by_user(user_id)
        user = db.get_user_by_id(user_id)
        return render_template('user_posts.html', content=user_content, logged_in=True, user=user)
    else:
        flash("You must be logged in to view your profile.")
        return redirect(url_for('login'))

# --- User Deletion Route ---
@app.route('/user/delete/<int:id>', methods=['POST'])
def delete_user(id):
    """Handle the user deletion process."""
    if request.form.get('_method') == 'DELETE':
        success = db.delete_user(id)
        if success:
            session.clear()  # Clear session after successful deletion
            flash('Your account has been deleted successfully.')
            return redirect(url_for('login'))
        else:
            flash('User not found or an error occurred.')
            return redirect(url_for('home'))
    else:
        flash('Invalid method for deleting user.')
        return redirect(url_for('home'))

# Function to send image info to RabbitMQ queue
def send_to_queue(content_id, image_path):
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='image_resize')
    message = json.dumps({"content_id": content_id, "image_path": image_path})
    channel.basic_publish(exchange='', routing_key='image_resize', body=message)
    connection.close()

# --- Add Content Route ---
@app.route('/add_content', methods=['POST'])
def add_content():
    """Add new content (posts) to the database."""
    if "user_id" not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    title = request.form['title']
    text = request.form.get('text')
    prompt = request.form.get('prompt')
    location = request.form['location']
    image = request.files.get('image')
    image_path = None

    # Handle image upload if provided
    if image:
        filename = secure_filename(image.filename)
        relative_path = os.path.join('images', filename).replace("\\", "/")
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_path = relative_path
        content_id = db.insert_content(user_id, title, text, image_path, location)

        # Send the image path to RabbitMQ for processing
        send_to_queue(content_id, image_path)

    # Handle user-provided text
    elif text:
        content_id = db.insert_content(user_id, title, text, None, location)

    # Handle prompt-based text generation
    if prompt:
        content_id = db.insert_content(user_id, title, prompt, None, location)
        send_prompt_to_queue(content_id, prompt)
    else:
        return redirect(url_for('home'))

    return redirect(url_for('home'))

# Function to send text generation prompt to RabbitMQ queue
def send_prompt_to_queue(content_id, prompt):
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='text_generation')
    message = json.dumps({"content_id": content_id, "prompt": prompt})
    channel.basic_publish(exchange='', routing_key='text_generation', body=message)
    connection.close()

# --- Fetch All Users Route ---
@app.route('/users', methods=['GET'])
def fetch_all_users():
    """Fetch and display all users."""
    users = db.get_all_users()
    return render_template('main_page.html', users=users, content=[], search_result=None, logged_in=True)

# --- Search User Route ---
@app.route('/search_user', methods=['POST'])
def search_user():
    """Search for a user by username and display their content."""
    username = request.form['username']
    user = db.get_user_by_username(username)

    if user:
        user_id = user[0]
        user_content = db.get_content_by_user(user_id)
        return render_template(
            'searched_user.html',
            search_result={"id": user[0], "username": user[1], "email": user[2], "content": user_content},
            users=[],
            content=[],
            logged_in=True
        )
    else:
        flash(f"No user found with username '{username}'.")
        return redirect(url_for('home'))

# --- Like Post Route ---
@app.route('/like_post/<int:content_id>', methods=['POST'])
def like_post(content_id):
    """Like a post."""
    if "user_id" in session:
        user_id = session['user_id']
        db.like_content(user_id, content_id)
        flash("Post liked!")
        return redirect(url_for('home'))
    else:
        flash("You need to be logged in to like a post.")
        return redirect(url_for('login'))

# --- Unlike Post Route ---
@app.route('/unlike_post/<int:content_id>', methods=['POST'])
def unlike_post(content_id):
    """Unlike a post."""
    if "user_id" in session:
        user_id = session['user_id']
        db.unlike_content(user_id, content_id)
        flash("Post unliked!")
        return redirect(url_for('home'))
    else:
        flash("You need to be logged in to unlike a post.")
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=(app.config['ENV'] == 'development'), host="0.0.0.0", port=5000)
