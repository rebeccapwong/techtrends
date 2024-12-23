import sqlite3
import logging
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

db_connection_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.debug = True
#app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    print(posts)
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
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

            return redirect(url_for('index'))

    return render_template('create.html')

#Healthz Endpoint
@app.route('/healthz', methods=['GET'])

def healthz():
    return jsonify(result="OK - healthy"), 200
    #return jsonify({"message":"OK - healthy"}), 200
    
with app.app_context():
    print(app.url_map)


#Metrics endpoint
@app.route('/metrics', methods=['GET'])

def metrics():
    global db_connection_count
    global metrics_response
    db_connection_count += 1
    print(db_connection_count)
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    post_count = len(posts)
    metrics_response = {"db_connection_count": db_connection_count, "post_count": post_count}
    return jsonify(metrics_response), 200

#Logging

logging.basicConfig(filename="app.log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/articles/<int:article_id>', methods=['GET'])

def get_article(article):
    if article == article.title:
        logging.info(f'Article"{article.title} retrieved')
        return jsonify(article, 200)
    else: 
        logging.error(f'Article with ID {article.title} not found (404 error)')
        return jsonify({"error": "Article not found"}), 404

@app.route('/about', methods = ['GET'])

def about_page():
    logging.info('About Us page retrieved.')
    return jsonify({"message": "About Us"}), 200

'''
@app.route('/articles', methods=['GET','POST'])
def create_article():
    # Simulate creating a new article
    data = request.get_json()
    if data is None:
        title = input("Enter title: ")
        content = input("Enter content: ")
        new_article = {title, content}
        logging.info(f'New article "{new_article.t}" created!')
    else:
        title = data.get('title')
        content = data.get('content')
        new_article = {title, content}
        logging.info(f'New article "{new_article[0]}" created!')
    return jsonify(new_article), 201
'''    


# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111', debug=True)
