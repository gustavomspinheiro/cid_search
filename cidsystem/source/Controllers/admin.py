from flask import flash, jsonify, request, render_template, url_for, redirect
from flask_login import login_user, current_user, logout_user, login_required

from cidsystem import app, db, bcrypt

#***RENDER ADMIN HOME***#
@app.route('/admin/home', methods=['GET'])
@login_required
def adminHome():
    return render_template('admin/home.html')