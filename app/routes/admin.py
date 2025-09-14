from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import User, Favorite
from app.db import db
from flask_login import login_required, current_user

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/panel')
@login_required
def admin_panel():
    if current_user.role != 'admin':
        flash("Unauthorized access", "danger")
        return redirect(url_for('auth.login'))

    users = User.query.all()
    return render_template('admin_panel.html', users=users)

@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash("Unauthorized access", "danger")
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully.", "success")
    return redirect(url_for('admin_bp.admin_panel'))

"""
@admin_bp.route('/favorites/<int:user_id>')
@login_required
def view_favorites(user_id):
    if current_user.role != 'admin':
        flash("Unauthorized access", "danger")
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(user_id)
    favorites = Favorite.query.filter_by(user_id=user.id).all()
    return render_template('admin_favorites.html', user=user, favorites=favorites)
    ß"""


@admin_bp.route('/update/<int:user_id>', methods=['GET'])
@login_required
def update_user_form(user_id):
    if current_user.role != 'admin':
        flash("Unauthorized access", "danger")
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(user_id)
    return render_template('update_user.html', user=user)


@admin_bp.route('/update/<int:user_id>', methods=['POST'])
@login_required
def update_user(user_id):
    if current_user.role != 'admin':
        flash("Unauthorized access", "danger")
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(user_id)

    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.email = request.form['email']
    user.username = request.form['username']
    user.gender = request.form['gender']
    user.country = request.form['country']
    user.city = request.form['city']
    user.role = request.form['role']

    db.session.commit()
    flash("User updated successfully.", "success")
    return redirect(url_for('admin_bp.admin_panel'))



@admin_bp.route('/create', methods=['GET'])
@login_required
def create_user_form():
    if current_user.role != 'admin':
        flash("Unauthorized access", "danger")
        return redirect(url_for('auth.login'))
    return render_template('create_user.html')


@admin_bp.route('/create', methods=['POST'])
@login_required
def create_user():
    if current_user.role != 'admin':
        flash("Unauthorized access", "danger")
        return redirect(url_for('auth.login'))

    from app.models import User 
    new_user = User(
        first_name=request.form['first_name'],
        last_name=request.form['last_name'],
        email=request.form['email'],
        username=request.form['username'],
        password=request.form['password'], 
        gender=request.form['gender'],
        country=request.form['country'],
        city=request.form['city'],
        role=request.form['role']
    )
    db.session.add(new_user)
    db.session.commit()
    flash("User created successfully.", "success")
    return redirect(url_for('admin_bp.admin_panel'))




