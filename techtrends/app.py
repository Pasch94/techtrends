import sqlite3
import sys
import logging

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# As suggested in the project review:
# Use the flask way of global variables
app.config['DBCOUNTER'] = 0
logger = None

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    app.config['DBCOUNTER'] += 1
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    if not post:
        return

    logger.info('Article {} retrieved'.format(post["title"]))
    return post

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      logger.info('Non existing article accessed')
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logger.info('About US page accessed')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            logger.info('Article {} created'.format(title))

            return redirect(url_for('index'))

    return render_template('create.html')

# Define the healtch check functionality
@app.route('/healthz')
def healthz():
    response = app.response_class(
                response=json.dumps({"result":"OK - healthy"}),
                status=200,
                mimetype='application/json'
                )
    return response

# Define metrics endpoint
@app.route('/metrics')
def metrics():
    # Get amount of posts
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    post_count = len(posts)

    json_response = json.dumps({
        "db_connection_count": app.config['DBCOUNTER'],
        "post_count": post_count
        })
                 
    response = app.response_class(
                response=json_response,
                status=200,
                mimetype='application/json'
                )
    return response

# start the application on port 3111
if __name__ == "__main__":
   global db_conn_count
   db_conn_count = 0
   log_stdout_handler = logging.StreamHandler(sys.stdout)
   log_stderr_handler = logging.StreamHandler(sys.stderr)
   logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=logging.DEBUG,
            datefmt='%Y-%m-%d %H:%M:%S'
            )
   logger = logging.getLogger(__name__)
   logger.addHandler(log_stdout_handler)
   logger.addHandler(log_stderr_handler)
   app.run(host='0.0.0.0', port='3111')
