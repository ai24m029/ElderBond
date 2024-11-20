from flask import Flask, request, jsonify, render_template, redirect, url_for
from DataBase import DataBaseAccess

app = Flask(__name__)

# API Endpoints

@app.route('/api/posts', methods=['POST'])
def add_post_api():
    data = request.json
    image = data.get('image')
    text = data.get('text')
    user = data.get('user')

    with DataBaseAccess() as db:
        db.add_post(image, text, user)

    return jsonify({'message': 'Post added successfully'}), 201


@app.route('/api/posts', methods=['GET'])
def list_posts_api():
    with DataBaseAccess() as db:
        posts = db.get_all_posts()

    results = [
        {'id': post[0], 'image': post[1], 'text': post[2], 'user': post[3], 'timestamp': post[4]}
        for post in posts
    ]
    return jsonify(results)


@app.route('/api/posts/search', methods=['GET'])
def search_posts_api():
    user = request.args.get('user')
    with DataBaseAccess() as db:
        db.cursor.execute("SELECT * FROM Posts WHERE user = ?", (user,))
        posts = db.cursor.fetchall()

    results = [
        {'id': post[0], 'image': post[1], 'text': post[2], 'user': post[3], 'timestamp': post[4]}
        for post in posts
    ]
    return jsonify(results)


# Frontend Routes

@app.route('/')
def index():
    # Get the 'user' query parameter from the URL
    user = request.args.get('user')

    with DataBaseAccess() as db:
        if user:
            # Search for posts by the specific user
            db.cursor.execute("SELECT * FROM Posts WHERE user = ?", (user,))
            posts = db.cursor.fetchall()
        else:
            # Fetch all posts if no user is specified
            posts = db.get_all_posts()

    return render_template('index.html', posts=posts)


@app.route('/add_post', methods=['POST'])
def add_post():
    image = request.form['image']
    text = request.form['text']
    user = request.form['user']

    with DataBaseAccess() as db:
        db.add_post(image, text, user)

    # Redirect back to the homepage
    return redirect('/')


@app.route('/search', methods=['GET'])
def search():
    user = request.args.get('user')
    posts = []

    if user:
        with DataBaseAccess() as db:
            db.cursor.execute("SELECT * FROM Posts WHERE user = ?", (user,))
            posts = db.cursor.fetchall()

    return render_template('index.html', posts=posts, search=True, search_user=user)


if __name__ == '__main__':
    app.run(debug=True)
