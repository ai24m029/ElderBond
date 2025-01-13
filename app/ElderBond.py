from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
import os
from DataBase import DataBaseAcess
import pika
import json

app = Flask(__name__)
# Flask environment
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')
app.config['SQLITE_DB_PATH'] = os.getenv('SQLITE_DB_PATH', 'social_media.db')
app.secret_key = "supersecretkey"  # Change this for production
bcrypt = Bcrypt(app)

db = DataBaseAcess()

# Directory to store uploaded images
UPLOAD_FOLDER = os.path.join('static', 'images')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
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
    """Login existing user."""
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
    """Signup a new user."""
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


@app.route('/user/delete/<int:id>', methods=['POST'])
def delete_user(id):
    """Handle the user deletion process."""
    if request.form.get('_method') == 'DELETE':
        success = db.delete_user(id)
        if success:
            session.clear()  # Clear the session after successful deletion
            flash('Your account has been deleted successfully.')
            return redirect(url_for('login'))  # Redirect to the login page after deletion
        else:
            flash('User not found or an error occurred.')
            return redirect(url_for('home'))  # Redirect back to the homepage if user is not found
    else:
        flash('Invalid method for deleting user.')
        return redirect(url_for('home'))  # Redirect back to homepage if method is not DELETE


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
    """Add a new post to the database."""
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
        relative_path = os.path.join('images', filename).replace("\\", "/")  # Save 'images/filename'
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_path = relative_path
        content_id = db.insert_content(user_id, title, text, image_path, location)
        print(f"[INFO] Post created with uploaded image (ID: {content_id})", flush=True)

        # Send the image path to RabbitMQ for processing
        send_to_queue(content_id, image_path)

    # Handle user-provided text
    elif text:
        content_id = db.insert_content(user_id, title, text, None, location)
        print(f"[INFO] Post created with user-written text (ID: {content_id})", flush=True)

    # Handle prompt-based text generation
    elif prompt:
        content_id = db.insert_content(user_id, title, prompt, None, location)
        print(f"[INFO] Post created with prompt for text generation (ID: {content_id})", flush=True)

        # Send the prompt to RabbitMQ for text generation
        send_prompt_to_queue(content_id, prompt)

    else:
        print("[ERROR] No valid content provided.", flush=True)
        return redirect(url_for('home'))

    return redirect(url_for('home'))



def send_prompt_to_queue(content_id, prompt):
    """Send the text generation prompt to RabbitMQ."""
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='text_generation')
    message = json.dumps({"content_id": content_id, "prompt": prompt})
    channel.basic_publish(exchange='', routing_key='text_generation', body=message)
    connection.close()


@app.route('/users', methods=['GET'])
def fetch_all_users():
    """Fetch all users."""
    users = db.get_all_users()
    return render_template('main_page.html', users=users, content=[], search_result=None, logged_in=True)


@app.route('/search_user', methods=['POST'])
def search_user():
    """Search for a user by username and display their content."""
    username = request.form['username']  # Get the username from the search form
    user = db.get_user_by_username(username)

    if user:
        # Fetch the user's content posts
        user_id = user[0]
        user_content = db.get_content_by_user(user_id)  # Get all posts by the user
        return render_template(
            'user_posts.html',
            search_result={
                "id": user[0],
                "username": user[1],
                "email": user[2],
                "content": user_content
            },
            users=[],  # Clear users to focus only on search result
            content=[],
            logged_in=True
        )
    else:
        flash(f"No user found with username '{username}'.")
        return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=(app.config['ENV'] == 'development'), host="0.0.0.0", port=5000)