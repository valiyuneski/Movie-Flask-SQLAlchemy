from flask import Flask, render_template
from data_manager import DataManager
from models import db, Movie
from sqlalchemy import inspect

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

@app.route('/')
def index():
    """Render the homepage with a list of users."""
    users = data_manager.get_users()
    return render_template('index.html', users=users)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)