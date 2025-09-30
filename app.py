from flask import Flask, render_template, request, redirect
from data_manager import DataManager
from models import db, Movie
from sqlalchemy import inspect
import os
from dotenv import load_dotenv
import requests

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

data_manager = DataManager()


# Only run this block once to create the database tables.
with app.app_context():
    inspector = inspect(db.engine)
    if not inspector.has_table("Movie"):  # replace with your table name
        print("Creating tables...")
        db.create_all()
        print("Tables created.")
    else:
        print("Tables already exist. Skipping.")


@app.route('/', methods=['GET'])
def index():
    """Render the homepage with a list of registered users GET by default"""
    users = data_manager.get_users()
    return render_template('index.html', users=users)


@app.route('/users', methods=['POST'])
def add_user():
    """Add a new user from form input."""
    # When the user submits the “add user” form, a POST request is made.
    # The server receives the new user info, adds it to the database, then redirects back to /.
    name = request.form.get('name')
    data_manager.create_user(name)
    return redirect('/')


@app.route('/users/<int:user_id>/movies', methods=['GET'])
def list_favorite_movies_by_user(user_id):
    """Retrieve and display a user's favorite movies."""
    movies = data_manager.get_movies(user_id)
    return render_template('movies.html', movies=movies, user_id=user_id)


@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_favorite_movie_by_user(user_id):
    """POST: Add a new movie to a user's favorites"""
    load_dotenv()
    name = request.form.get('name')
    params = {'t': name, 'apikey': os.getenv("API_KEY")}

    try:
        response = requests.get('https://www.omdbapi.com/', params=params, timeout=5)
        response.raise_for_status()
        movie_data = response.json()

        if movie_data.get("Response") != "True":
            return render_template('error.html', message="Movie not found in OMDb API."), 404

        movie = {
            "name": movie_data['Title'],
            "director": movie_data['Director'],
            "year": movie_data['Year'],
            "poster_url": movie_data['Poster'],
            "user_id": user_id
        }
        data_manager.add_movie(movie)

    except requests.RequestException as e:
        return render_template('error.html', message=f"OMDb request failed: {e}"), 500

    # After adding, show updated list
    movies = data_manager.get_movies(user_id)
    return render_template('movies.html', movies=movies, user_id=user_id)


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie(user_id, movie_id):
    """Update the title of a user's movie."""
    # Modify the title of a specific movie in a user’s list, without depending on OMDb 
    # for corrections.
    name = request.form.get('name')
    data_manager.update_movie(movie_id, user_id, name)
    return redirect(f'/users/{user_id}/movies')


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    """DRemove a specific movie from a user’s favorite movie list.."""
    data_manager.delete_movie(movie_id, user_id)
    return redirect(f'/users/{user_id}/movies')


@app.errorhandler(404)
def page_not_found(error):
    """Render a custom 404 error page."""
    return render_template('404.html', message="Oops! Page not found."), 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)