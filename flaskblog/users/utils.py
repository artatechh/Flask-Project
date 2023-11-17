import os
import secrets
from PIL import Image
from flask import url_for
from flask_mail import Message
from flaskblog import  mail
from flask import current_app


def saveimage(form_image):
	random_hax = secrets.token_hex(8)
	_ , f_ext = os.path.splitext(form_image.filename)
	picture_fn = random_hax + f_ext
	picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
	output_size = (125,125)
	i = Image.open(form_image)
	i.thumbnail(output_size)	
	i.save(picture_path)
	return picture_fn




def deleteimage(image_filename):
	if image_filename != 'default.jpg':
		image_path = os.path.join(current_app.root_path, 'static/profile_pics', image_filename)
		if os.path.exists(image_path):
			os.remove(image_path)
			


def send_reset_email(user):
    token = user.get_reset_token()
    print(url_for('users.resetpassword', token=token, _external=True))
    msg = Message('Password Reset Request',
                 sender='artatechh@gmail.com',
                 recipients=[user.email])
    msg.body = f"To reset your password, visit the following link:{url_for('users.resetpassword', token=token, _external=True)} If you did not make this request then simply ignore this email and no changes will be made."
    
    mail.send(msg)