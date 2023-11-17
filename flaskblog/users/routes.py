from flask import Blueprint
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db, bcrypt
from flaskblog.models import User, Post
from flaskblog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm, PasswordRForm, ResetPForm)
from flaskblog.users.utils import saveimage, send_reset_email, deleteimage
users = Blueprint('users', __name__)



@users.route('/register', methods = ['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash('Your account has been created! You are now able to log in', 'success')
		return redirect(url_for('users.login'))
	return render_template("register.html", title="register", form=form)




@users.route('/login', methods = ['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			
			return redirect(next_page) if next_page else redirect(url_for('main.home'))
		else:
			flash('login unsuccessful. Pls Check Username and password', 'danger' )
	return render_template("login.html", title="login", form=form)





@users.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('main.home'))


@users.route('/account', methods = ['GET', 'POST'])
@login_required
def account():
	form =  UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			deleteimage(current_user.image_file)
			picture_file = saveimage(form.picture.data)
			current_user.image_file = picture_file
		current_user.email = form.email.data
		current_user.username = form.username.data
		db.session.commit()
		flash('your account has been updated !', 'success' )
		redirect(url_for('users.account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	return render_template("account.html", title="my account", image_file=image_file, form=form )







@users.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()

    posts = Post.query.filter_by(author=user)\
	.order_by(Post.date_posted.desc())\
	.paginate(page=page, per_page=6)

    return render_template('user_posts.html', posts=posts, title='User Posts', user=user)








@users.route('/reset_request', methods=['GET', 'POST'])
def resetrequest():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = PasswordRForm()
	if form.validate_on_submit():
		user=User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('Reset password request sent to your email.', 'info')
		return redirect(url_for('users.login'))
			
	return render_template('Rpassword.html', title='Forgot password', form=form)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def resetpassword(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    user = User.verify_reset_token(token)

    if user is None:
        flash('That is an invalid or expired token.', 'warning')
        return redirect(url_for('users.resetrequest'))

    form = ResetPForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.add(user)
        db.session.commit()

        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))

    return render_template('Reset_token.html', title='reset password', form=form)
	