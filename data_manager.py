from models import User, Movie
from models import db
from sqlalchemy.exc import SQLAlchemyError
import logging

class DataManager:
    """Handles database operations for users and movies."""

    def create_user(self, input_name):
        """Create and store a new user."""
        try:
            new_user = User(name=input_name)
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"Error creating user: {e}")
            return None

    def get_users(self):
        """Retrieve all users from the database."""
        try:
            return db.session.query(User).all()
        except SQLAlchemyError as e:
            logging.error(f"Error fetching users: {e}")
            return []


    def get_user_by_id(self, input_user_id) -> str:
        """Retrieve a user's name by their ID."""
        try:
            user = db.session.query(User).filter_by(id=input_user_id).first()
            return user.name if user else "Unknown User"
        except SQLAlchemyError as e:
            logging.error(f"Error fetching user by ID: {e}")
            return "Unknown User"
        

    def get_movies(self, input_user_id):
        """Retrieve all movies for a given user."""
        try:
            return db.session.query(Movie).filter_by(user_id=input_user_id).all()
        except SQLAlchemyError as e:
            logging.error(f"Error fetching movies: {e}")
            return []

    def add_movie(self, input_movie):
        """Add a new movie to the database."""
        try:
            new_movie = Movie(**input_movie)
            db.session.add(new_movie)
            db.session.commit()
            return new_movie
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"Error adding movie: {e}")
            return None

    def update_movie(self, input_movie_id, input_user_id, input_new_title):
        """Update the title of a user's movie."""
        try:
            updated = db.session.query(Movie).filter(
                Movie.id == input_movie_id,
                Movie.user_id == input_user_id
            ).update({"name": input_new_title})
            db.session.commit()
            return updated  # returns number of updated rows
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"Error updating movie: {e}")
            return 0

    def delete_movie(self, input_movie_id, input_user_id):
        """Delete a movie belonging to a user."""
        try:
            deleted = db.session.query(Movie).filter(
                Movie.id == input_movie_id,
                Movie.user_id == input_user_id
            ).delete()
            db.session.commit()
            return deleted  # returns number of deleted rows
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"Error deleting movie: {e}")
            return 0