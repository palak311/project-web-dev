from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user, login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from flask import session

app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cinescope.db'
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Movie Model
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    release_date = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String, nullable=True)
    poster_url = db.Column(db.String(300))

# Review Model
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    movie = db.relationship('Movie', backref=db.backref('watchlisted_by', lazy=True))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return f"Welcome, user {session['user_id']}!"

@app.route("/watchlist")
@login_required
def watchlist():
    if 'user_id' not in session:
        flash("You need to log in first.", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    watchlist_movies = db.session.query(Movie).join(Watchlist).filter(Watchlist.user_id == user_id).all()
    print(f"User {user_id} Watchlist: {watchlist_movies}")
    return render_template('watchlist.html', movies=watchlist_movies)

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

# Routes
@app.route('/', endpoint='home')
def home():
    page = request.args.get('page', 1, type=int)
    movies = Movie.query.paginate(page=page, per_page=6)
    return render_template('index.html', movies=movies)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash("All fields are required!", "danger")
            return render_template('register.html', username=username, email=email)

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "warning")
            return render_template('register.html', username=username, email=email)

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            login_user(user)
            flash("login successful", "success")
            return redirect(url_for("home"))
        else:
            print("Invalid credentials!")
            flash('Invalid email or password', 'danger')

    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)
    flash("Logged out successfully!", "info")
    return redirect(url_for('home'))

@app.route('/movie/<int:movie_id>')
def movie_page(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    reviews = Review.query.filter_by(movie_id=movie_id).all()
    avg_rating = db.session.query(db.func.avg(Review.rating)).filter(Review.movie_id == movie_id).scalar()
    avg_rating = round(avg_rating, 1) if avg_rating else "No ratings yet"
    related_movies = Movie.query.filter(Movie.genre == movie.genre, Movie.id != movie.id).limit(4).all()
    return render_template("moviepage.html", movie=movie, reviews=reviews, avg_rating=avg_rating, related_movies=related_movies)

@app.route("/movie/<int:movie_id>/add_review", methods=["POST"])
@login_required
def add_review(movie_id):
    content = request.form.get("review_content")
    rating = request.form.get("rating", type=int)

    if not (1 <= rating <= 10):
        flash("Rating must be between 1 and 10", "danger")
        return redirect(url_for("movie_page", movie_id=movie_id))

    if content:
        new_review = Review(movie_id=movie_id, user_id=current_user.id, content=content, rating=rating)
        db.session.add(new_review)
        db.session.commit()
        flash("Review added successfully!", "success")

    return redirect(url_for("movie_page", movie_id=movie_id))

@app.route('/add_to_watchlist/<int:movie_id>', methods=['POST'])
@login_required
def add_to_watchlist(movie_id):
    if 'user_id' not in session:
        flash("You need to log in first.", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    movie = Movie.query.get(movie_id)
    if movie:
        print(f"Adding Movie ID {movie.id} to Watchlist")
        existing_entry = Watchlist.query.filter_by(user_id=user_id, movie_id=movie.id).first()
        if existing_entry:
            print("Movie already in watchlist!")
            flash("Movie already in watchlist!", "info")
        else:
            watchlist_entry = Watchlist(user_id=user_id, movie_id=movie.id)
            db.session.add(watchlist_entry)
            db.session.commit()
            print(f"Movie {movie.id} added successfully!")
            flash(f"{movie.title} added to your watchlist!", "success")
    else:
        print("Movie not found!")

    return redirect(url_for('home'))


@app.route('/api/movies')
def api_movies():
    movies = Movie.query.all()
    return jsonify([{ 'title': m.title, 'genre': m.genre, 'release_date': m.release_date } for m in movies])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

with app.app_context():
    movies = Movie.query.all()
    print(movies)

with app.app_context():
    movie = Movie(title="Inception", genre="Sci-Fi", release_date="2010", poster_url="https://image.url")
    db.session.add(movie)
    db.session.commit()

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.secret_key = 'your_secret_key'
