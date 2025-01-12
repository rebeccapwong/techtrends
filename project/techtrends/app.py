import sqlite3
import logging
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import sys

db_connection_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID

def get_post(post_id):
    global db_connection_count
    db_connection_count += 1
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'your password'

#Set up Logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create handlers
c_handler = logging.StreamHandler(sys.stderr)  # For console output
f_handler = logging.FileHandler('app.log', mode='a', delay=False)  # For file output

# Set level for handlers
c_handler.setLevel(logging.DEBUG)
f_handler.setLevel(logging.DEBUG)

# Create formatters and add them to handlers
c_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)

#logging.basicConfig(filename="app.log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


# Define the main route of the web application 
@app.route('/')
def index():
    global db_connection_count
    db_connection_count += 1
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    logger.info('Home page request successful.')
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      logger.info('404 not found. Try another request.')
      return render_template('404.html'), 404
    
    else:
      logger.info('Post request successful.')
      return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about', methods = ['GET'])
def about():
    return render_template('about.html')

@app.route('/about', methods = ['GET'])
def about_page():
    logger.info('About Us request successful.')
    return jsonify({"message": "About Us"}), 200

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            global db_connection_count
            db_connection_count += 1
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))
        
    logger.info('Create request successful.')
    return render_template('create.html')

#Healthz Endpoint
@app.route('/healthz', methods=['GET'])

def healthz():

    ## log line
    logger.info('Health request successful.')
 
    return jsonify(result="OK - healthy"), 200
    
with app.app_context():
    print(app.url_map)


#Metrics endpoint
@app.route('/metrics', methods=['GET'])

def metrics():
    global db_connection_count
    global metrics_response
    db_connection_count += 1
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    post_count = len(posts)
    metrics_response = {"db_connection_count": db_connection_count, "post_count": post_count}
    print(metrics_response)
    
    ## log line
    logger.info('Metrics request successful.')

    return jsonify(metrics_response), 200    

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111', debug=True)
