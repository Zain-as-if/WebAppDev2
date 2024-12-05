from flask import render_template, request, url_for, redirect, flash, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app import app, db, bcrypt, admin
from flask_admin.contrib.sqla import ModelView
from app.models import User, Movie, Review
from app.forms import RegisterForm, LoginForm, ReviewForm

# just used for viewing, can't add
# error when adding: AttributeError: 'tuple' object has no attribute 'items'
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Movie, db.session))
admin.add_view(ModelView(Review, db.session))

@app.route('/')
def home():
    return render_template('home.html')

"""
    User login system
    - Register
    - Login
    - Logout
    - Profile
"""
@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    watched_movies = current_user.watched_movies
    user_reviews = Review.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', username=current_user.username, watched_movies=watched_movies, reviews=user_reviews)

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('profile'))
    
    return render_template('login.html', form=form)

@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

"""
    Movie Pages
    - List
    - Specific Movie Page
"""
@app.route('/movielist', methods=['GET'])
def movielist():
    movies = Movie.query.all()
    return render_template('movie_list.html', movies=movies)

@app.route('/movie/<int:id>', methods=['POST', 'GET'])
def movie(id):
    movie = Movie.query.get_or_404(id)
    reviews = Review.query.filter_by(movie_id=id).all()
    return render_template('movie.html', movie=movie, reviews=reviews)

@app.route('/movie/<int:id>/toggle_watchlist', methods=['POST'])
@login_required
def toggle_watchlist(id):
    movie = Movie.query.get_or_404(id)

    if movie in current_user.watched_movies:
        current_user.watched_movies.remove(movie)
        db.session.commit()
        message = 'Movie has been removed from your watchlist'
    else:
        current_user.watched_movies.append(movie)
        db.session.commit()
        message = 'Movie has been added to your watchlist'

    in_watchlist = movie in current_user.watched_movies

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'message': message, 'in_watchlist': in_watchlist})

    flash(message)
    return redirect(url_for('movie', id=movie.id))

"""
    Reviews
"""
@app.route('/movie/<int:id>/write_review', methods=['POST', 'GET'])
@login_required
def writereview(id):
    movie = Movie.query.get_or_404(id)
    form = ReviewForm()

    if form.validate_on_submit():
        new_review = Review(
                content=form.content.data,
                rating=form.rating.data,
                user_id=current_user.id,
                movie_id=movie.id
        )
        db.session.add(new_review)
        db.session.commit()
        flash('Your review has been added!', 'success')
        return redirect(url_for('movie', id=movie.id))

    reviews = Review.query.filter_by(movie_id=movie.id).all()
    return render_template('writereview.html', movie=movie, form=form, reviews=reviews)

@app.route('/review/<int:id>/delete', methods=['POST'])
@login_required
def delete_reviews(id):
    review = Review.query.get_or_404(id)
    if review.user_id == current_user.id:
        db.session.delete(review)
        db.session.commit()
        flash('Your review has been deleted!', 'success')
    else:
        flash('You are not authorised to delete this review.', 'danger')

    return redirect(url_for('profile'))

@app.route('/review/<int:id>/edit', methods=['POST', 'GET'])
@login_required
def edit_review(id):
    review = Review.query.get_or_404(id)

    if review.user_id != current_user.id:
        flash('You are not authorised to edit this review.', 'danger')
        return redirect(url_for('profile'))
    
    form = ReviewForm(obj=review)

    if form.validate_on_submit():
        review.content=form.content.data
        review.rating=form.rating.data
        db.session.commit()
        flash('Your review has been updated!', 'success')
        return redirect(url_for('profile'))

    return render_template('edit_review.html', form=form, review=review)
