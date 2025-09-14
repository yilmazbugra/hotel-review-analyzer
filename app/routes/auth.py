from flask import Blueprint, render_template, request, redirect, flash
import logging
from app.db import get_db_connection
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.db import db

auth = Blueprint('auth', __name__)

@auth.route('/')
def first_entry():
    return render_template('first_entry.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            username = request.form['username']
            password = request.form['password']  
            gender = request.form['gender']
            country = request.form['country']
            city = request.form['city']
            role = request.form['role']

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO users (first_name, last_name, email, username, password, gender, country, city, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (first_name, last_name, email, username, password, gender, country, city, role)
            )
            connection.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect('/auth/login')
        except Exception as e:
            logging.error(f"Registration error: {e}")
            flash('An error occurred during registration.', 'danger')
        finally:
            connection.close()

    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            user = User.query.filter_by(username=username).first()

            if user and password == user.password:  
                login_user(user)
                flash('Login successful!', 'success')

                if user.role == 'staff':
                    return redirect('/auth/owner_index')
                elif user.role == 'user':
                    return redirect('/auth/user_index')
                elif user.role == 'admin':
                    return redirect('/admin/panel')
                else:
                    flash('Unknown role.', 'danger')
                    return redirect('/auth/login')
            else:
                flash('Invalid username or password.', 'danger')
        except Exception as e:
            logging.error(f"Login error: {e}")
            flash('Login error. Please try again.', 'danger')

    return render_template('login.html')

@auth.route('/logout')
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect('/auth/login')

"""@auth.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html', username=current_user.username)
    """

@auth.route('/owner_index')
@login_required
def owner_index():
    if current_user.role != 'staff':
        flash('You do not have permission to access this page.', 'danger')
        return redirect('/auth/login')
    return render_template('owner_index.html')

@auth.route('/user_index')
@login_required
def user_index():
    if current_user.role != 'user':
        flash('You do not have permission to access this page.', 'danger')
        return redirect('/auth/login')
    return render_template('user_index.html')


@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        username = request.form.get('username')
        gender = request.form.get('gender')
        country = request.form.get('country')
        city = request.form.get('city')

        try:
            
            user = current_user
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.gender = gender
            user.country = country
            user.city = city

            db.session.commit()
            flash('Profile updated successfully.', 'success')
        except Exception as e:
            flash('An error occurred while updating profile.', 'danger')

    
    return render_template('profile.html', user=current_user)


@auth.route('/profile/delete', methods=['POST'])
@login_required
def delete_profile():
    try:
        user = current_user
        logout_user()
        db.session.delete(user)
        db.session.commit()
        flash('Your profile has been deleted.', 'success')
        return redirect(url_for('auth.first_entry'))
    except Exception as e:
        flash('An error occurred while deleting your profile.', 'danger')
        return redirect(url_for('auth.profile'))